import logging
import colander

from grano.core import db, celery
from grano.lib.data import CSVImporter
from grano.model import Pipeline, File, Attribute
from grano.logic import pipelines, entities, loader
from grano.logic.references import FileRef, ProjectRef
from grano.logic.validation import Invalid


log = logging.getLogger(__name__)
MODES = ['aliases', 'entities', 'relations']


class ImportBaseValidator(colander.MappingSchema):
    file = colander.SchemaNode(FileRef())
    project = colander.SchemaNode(ProjectRef())
    source_url = colander.SchemaNode(colander.String(),
        empty=None, missing=None)
    mode = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(MODES))


def make_importer(project, account, data):
    """ Create an importer pipeline to represent the data
    import process which will be executed. """

    validator = ImportBaseValidator()
    sane = validator.deserialize(data)

    # TODO: validate mapping. 
    config = {
        'mode': sane.get('mode'),
        'file': sane.get('file').id,
        'source_url': sane.get('source_url'),
        'mapping': data.get('mapping'),
        'relation_schema': data.get('relation_schema')
    }
    pipeline = pipelines.create(project, 'import',
        sane.get('file').file_name, config, account)
    run_importer.delay(pipeline.id)
    return pipeline


@celery.task
def run_importer(pipeline_id):
    """ Perform a raw data import with a given mode. """

    pipeline = Pipeline.by_id(pipeline_id)
    pipelines.start(pipeline)

    mode = pipeline.config.get('mode')
    file_id = pipeline.config.get('file')
    file_ = File.by_id(file_id)
    if file_ is None:
        piplines.log_error(pipeline, 'File object deleted: %s' % file_id)
    elif mode == 'aliases':
        import_aliases(pipeline, file_.fh)
    else:
        import_objects(pipeline, file_.fh)

    pipelines.finish(pipeline)


def _row_source_url(pipeline, row):
    """ Determine the best available source URL for the given 
    row of data. """
    for k, v in pipeline.config.get('mapping', {}).items():
        if v.get('attribute') == '_source_url':
            value = row.get(k, '').strip()
            if len(value):
                return value
    source_url = pipeline.config.get('source_url')
    if source_url is not None and len(source_url.strip()):
        return source_url
    return None


def import_aliases(pipeline, fh):
    """ Import aliases from a CSV source. This will not create
    new entities, but re-name existing entities or merge two
    entities if one's name is given as an alias for the other. """

    importer = CSVImporter(fh)
    canonical_column, alias_column = None, None
    for k, v in pipeline.config.get('mapping', {}).items():
        if v.get('attribute') == 'alias':
            alias_column = k
        elif v.get('attribute') == 'canonical':
            canonical_column = k

    for i, row in enumerate(importer):
        source_url = _row_source_url(pipeline, row)
        entities.apply_alias(pipeline.project, pipeline.author,
            row.get(canonical_column),
            row.get(alias_column), 
            source_url=source_url)
        
        if i % 100 == 0:
            percentage = int((float(i) / max(1, len(importer)))*100)
            pipeline.percent_complete = percentage
            db.session.commit()


def _mapping_schemata(project, mapping, obj):
    schemata = set()
    for column, spec in mapping.items():
        attr = spec.get('attribute')
        if not attr or not len(attr.strip()):
            continue
        if spec.get('object') == obj:
            attr_obj = project.get_attribute('entity', attr)
            if attr_obj is not None:
                schemata.add(attr_obj.schema.name)
    return list(schemata)


def import_objects(pipeline, fh):
    """ Import objects - either individual entities or relations 
    and their involved entities (the target and source) - from a 
    CSV file. """

    # Code is a bit ugly as this handles two cases at once: 
    #  mode 'relations' where we import a source, target and relation
    #  mode 'entities' where we only import a single entity

    mode = pipeline.config.get('mode')
    mapping = pipeline.config.get('mapping')
    relation_schema = pipeline.config.get('relation_schema')

    # This will identify the unique set of schemata per entity.
    source_schemata = _mapping_schemata(pipeline.project, mapping, 'source')
    target_schemata = _mapping_schemata(pipeline.project, mapping, 'target')
    entity_schemata = _mapping_schemata(pipeline.project, mapping, '')

    importer = CSVImporter(fh)
    loader_ = loader.Loader(pipeline.project.slug, account=pipeline.author,
        ignore_errors=False)

    for i, row in enumerate(importer):
        try:
            source_url = _row_source_url(pipeline, row)
            rel_data = {}
            source = loader_.make_entity(source_schemata, source_url=source_url)
            target = loader_.make_entity(target_schemata, source_url=source_url)
            entity = loader_.make_entity(entity_schemata, source_url=source_url)

            # Try to assign each column to the appropriate object in this
            # loader. 
            for column, spec in mapping.items():
                attr = spec.get('attribute')
                obj = spec.get('object')
                value = row.get(column)

                if not attr or not len(attr.strip()):
                    continue

                if mode == 'entities':
                    entity.set(attr, value)
                elif obj == 'relation':
                    rel_data[attr] = value
                elif obj == 'source':
                    source.set(attr, value)
                elif obj == 'target':
                    target.set(attr, value)

            # Relation can only be saved once the entities are available,
            # hence we're storing the relation property values and now 
            # making the whole thing.
            if mode == 'relations':
                source.save()
                target.save()
                rel = loader_.make_relation(relation_schema, source,
                    target, source_url=source_url)
                for k, v in rel_data.items():
                    rel.set(k, v)
                rel.save()
            else:
                entity.save()
            
            # indicate progress, and commit every now and then.
            if i % 100 == 0:
                percentage = int((float(i) / max(1, len(importer)))*100)
                pipeline.percent_complete = percentage
                loader_.persist()
        except Invalid, inv:
            pipelines.log_warn(pipeline, unicode(inv), 'Invalid data', inv.as_dict())
        except Exception, exc:
            pipelines.log_error(pipeline, unicode(exc), 'Error', {})

