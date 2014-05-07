# coding: utf-8
from StringIO import StringIO
import unicodecsv

from grano.logic import Loader
from grano.logic.schemata import import_schema


# This source URL will be applied to all properties without their own lineage:
DEFAULT_SOURCE_URL = 'http://www.opennews.org/'

DATA = """fellow_name,twitter_handle,start_date,end_date,organization_name,organization_url
Ben Chartoff,,2014-02-01,2014-12-01,Washington Post,http://www.washingtonpost.com/
Mark Boas,maboas,2012-02-01,2012-12-01,Al Jazeera English,http://www.aljazeera.com/
Noah Veltman,veltman,2013-02-01,2013-12-01,BBC,http://www.bbc.co.uk
Laurian Gridinoc,gridinoc,2012-02-01,2012-12-01,BBC,http://www.bbc.co.uk
Sonya Song,sonya2song,2013-02-01,2013-12-01,Boston Globe,http://www.bostonglobe.com/
Dan Schultz,slifty,2012-02-01,2012-12-01,Boston Globe,http://www.bostonglobe.com/
Gabriela Rodriguez,gaba,2014-02-01,2014-12-01,La Nacion,http://www.lanacion.com
Manuel Aristarán,manuelaristaran,2013-02-01,2013-12-01,La Nacion,http://www.lanacion.com
Harlo Holmes,harlo,2014-02-01,2014-12-01,New York Times,http://www.nytimes.com
Brian Abelson,brianabelson,2013-02-01,2013-12-01,New York Times,http://www.nytimes.com
Brian Jacobs,btjakes,2014-02-01,2014-12-01,ProPublica,http://www.propublica.org
Mike Tigas,mtigas,2013-02-01,2013-12-01,ProPublica,http://www.propublica.org
Friedrich Lindenberg,pudo,2013-02-01,2013-12-01,Spiegel Online,http://www.spiegel.de/
Marcos Vanetta,malev,2014-02-01,2014-12-01,Texas Tribune,http://www.texastribune.org/
Stijn Debrouwere,stdbrouw,2013-02-01,2013-12-01,The Guardian,http://www.theguardian.com/uk
Nicola Hughes,DataMinerUK,2012-02-01,2012-12-01,The Guardian,http://www.theguardian.com/uk
Aurelia Moser,auremoser,2014-02-01,2014-12-01,Ushahidi / Internews Kenya,http://www.ushahidi.com/
Annabel Church,annabelchurch,2013-02-01,2013-12-01,Zeit Online,http://www.zeit.de/index
Cole Gillespie,theCole,2012-02-01,2012-12-01,Zeit Online,http://www.zeit.de/index"""

SCHEMATA = """
- name: fellow
  label: An OpenNews fellow
  obj: entity
  hidden: no
  attributes:
    - name: twitter_handle
      label: Twitter handle

- name: news_organization
  label: A news organization
  obj: entity
  hidden: no
  attributes:
    - name: url
      label: URL

- name: fellowship
  label: A Fellowship
  label_in: Was hosted by
  label_out: Worked for
  obj: relation
  attributes:
    - name: start_date
      label: Start date
    - name: end_date
      label: End date
"""


def create_fixtures():
    loader = Loader('opennews', project_label='Open News',
                    project_settings={},
                    source_url=DEFAULT_SOURCE_URL)
    
    import_schema(loader.project, StringIO(SCHEMATA))

    reader = unicodecsv.reader(StringIO(DATA))
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
