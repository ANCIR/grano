import logging

from grano.core import db
from grano.model import Entity, Relation, Project
from grano.logic import entities, relations, projects, accounts
from grano.logic.validation import Invalid


log = logging.getLogger(__name__)


class ObjectLoader(object):
    # Abstract parent

    def _setup(self, loader, schemata):
        self.loader = loader
        self.schemata = schemata
        self.properties = {}
        self.update_criteria = set()

    def unique(self, name, only_active=True):
        """ Define a unique field for this entity or relation. Each unique 
        key will be used to decide whether a record already exists and can 
        be updated, or whether a new one must be created.

        :param name: The property name of the unique field.
        :param only_active: If set to ``False``, the check will include all 
            historic values of the property as well as the current value. 
        """
        self.update_criteria.add((name, only_active))

    def set(self, name, value, source_url=None):
        """ Set the value of a given property, optionally by attributing a 
        source URL. 

        :param name: The property name. This must be defined as part of one
            of the schemata that the entity or relation is associated with. 
        :param value: The value to be set for this property. If it is
            ``None``, the property will not be set, but existing values of 
            will be marked as inactive.
        :param source_url: A URL which will be set as the origin of this 
            information.
        """
        source_url = source_url or self.source_url
        #if source_url is None:
        #    log.warning('No source for property %s.', name)
        self.properties[name] = {
            'name': name,
            'value': value if value is None else unicode(value),
            'source_url': source_url,
            'active': True
            }


class EntityLoader(ObjectLoader):
    """ A factory object for entities, used to set the schemata and 
    properties for an entity. """

    def __init__(self, loader, schemata, source_url=None):
        self._setup(loader, schemata)
        self.unique('name', only_active=False)
        self.source_url = source_url
        self._entity = None


    @property
    def entity(self):
        if self._entity is None:
            self.save()
        return self._entity


    def save(self):
        """ Save the entity to the database. Do this only once, after all
        properties have been set. """

        # fetch existing:
        q = Entity.all()
        q = q.filter(Entity.project==self.loader.project)
        for name, only_active in self.update_criteria:
            value = self.properties.get(name).get('value')
            attr = self.loader.project.get_attribute('entity', name)
            q = Entity._filter_property(q, [attr], value,
                only_active=only_active)

        entity = q.first()

        try:
            data = {
                'project': self.loader.project,
                'author': self.loader.account,
                'schemata': self.schemata,
                'properties': self.properties
            }
            self._entity = entities.save(data, entity=entity)

        except Invalid, inv:
            if not self.loader.ignore_errors:
                raise
            log.warning("Validation error: %r", inv.asdict())


class RelationLoader(ObjectLoader):
    """ A factory object for relations, used to construct a relation by setting
    its schema, source entity, target entity and a set of properties. """
    
    def __init__(self, loader, schema, source, target, source_url=None):
        self._setup(loader, [schema])
        self.source_url = source_url
        self.source = source 
        self.target = target


    def save(self):
        """ Save the relation to the database. Do this only once, after all
        properties have been set. """

        # fetch existing:
        q = Relation.all()
        q = q.filter(Relation.project==self.loader.project)
        q = q.filter(Relation.source==self.source.entity)
        q = q.filter(Relation.target==self.target.entity)

        for name, only_active in self.update_criteria:
            value = self.properties.get(name).get('value')
            attr = self.loader.project.get_attribute('relation', name)
            q = Entity._filter_property(q, [attr], value,
                only_active=only_active)

        relation = q.first()

        try:
            data = {
                'project': self.loader.project,
                'author': self.loader.account,
                'schema': self.schemata.pop(),
                'properties': self.properties,
                'source': self.source.entity,
                'target': self.target.entity
            }
            self._relation = relations.save(data, relation=relation)
        except Invalid, inv:
            if not self.loader.ignore_errors:
                raise
            log.warning("Validation error: %r", inv.asdict())
        

class Loader(object):
    """ A loader is a factory object that can be used to make entities and 
    relations in the database. It will perform some validation and handle 
    database transactions. """

    def __init__(self, project_slug, source_url=None, project_label=None,
            project_settings=None, account=None, ignore_errors=True):
        self.source_url = source_url
        self.account = account or accounts.console_account()
        self.ignore_errors = ignore_errors
        
        project = Project.by_slug(project_slug)
        project_settings = project_settings or (project.settings if project else {})
        project_label= project_label or (project.label if project else project_slug)
        self.project = projects.save({
            'slug': project_slug,
            'author': self.account,
            'label': project_label,
            'settings': project_settings
            }, project=project)
        
        #self.entities = []
        #self.relations = []


    def make_entity(self, schemata, source_url=None):
        """ Create an entity loader, i.e. a construction helper for entities.

        :param schemata: A list of schema names for all the schemata that the entity 
            should be associated with.
        :param source_url: A URL which will be made the default source for all 
            properties defined on this entity.

        :returns: :py:class:`EntityLoader <grano.logic.loader.EntityLoader>`
        """
        entity = EntityLoader(self, schemata,
            source_url=source_url or self.source_url)
        #self.entities.append(entity)
        return entity


    def make_relation(self, schema, source, target, source_url=None):
        """ Create a relation loader, i.e. a construction helper for relations.

        :param schema: A schema name for the relation.
        :param source: An :py:class:`EntityLoader <grano.logic.loader.EntityLoader>` 
            which has been used to construct the source entity. 
        :param target: A second :py:class:`EntityLoader <grano.logic.loader.EntityLoader>` 
            which has been used to construct the target entity. Cannot be identical to
            the source.
        :param source_url: A URL which will be made the default source for all 
            properties defined on this entity.

        :returns: :py:class:`RelationLoader <grano.logic.loader.RelationLoader>`
        """

        relation = RelationLoader(self, schema, source, target,
            source_url=source_url or self.source_url)
        #self.relations.append(relation)
        return relation


    def persist(self):
        """ Save the created entiites and relations, i.e. commit the database
        transaction. """
        db.session.commit()
