# coding: utf-8
from normality import normalize
import csv
import normality
from grano.logic import Loader
rows = ["id", "name", "sort_name", "email", "twitter", "facebook", "group", "group_id", "area_id", "area", "chamber", "term", "start_date", "end_date", "image", "gender"]


if __name__ == "__main__":

    loader = Loader('senegal', project_label='Senegal')
    person = loader.make_entity("politician")


    with open('senegal/senegal-politicians.csv', 'r') as csvfile:
        records_reader = csv.reader(csvfile, delimiter=",")
        for row in records_reader:
            for x in range(0, len(rows)):
                #print "%s :: %s" % (rows[x], row[x])
                if row[x]:
                    val = normalize(str(row[x]))
                    person.set( rows[x], val )
            person.save()
        loader.persist()
