from grano.logic import Loader
import unicodecsv
 
# This source URL will be applied to all properties without their own lineage:
DEFAULT_SOURCE_URL = 'http://www.opennews.org/'
 
# Any settings (free-form dict):
PROJECT_SETTINGS = {}
 
loader = Loader('opennews', project_label='opennews',
    project_settings=PROJECT_SETTINGS, source_url=DEFAULT_SOURCE_URL)
 
reader = unicodecsv.reader(open('fellows.csv'))
reader.next()
 
for record in reader:
    fellow = loader.make_entity(['fellow'])
    fellow.set('name', record[0])
    fellow.set('twitter_handle', record[1])
    fellow.save()
 
    news_org = loader.make_entity(['news_organization'])
    news_org.set('name', record[4])
    news_org.set('url', record[5])
    news_org.save()
 
    fellowship = loader.make_relation('fellowship', fellow, news_org)
    fellowship.set('start_date', record[2])
    fellowship.set('end_date', record[3])
    fellowship.save()

loader.persist()
