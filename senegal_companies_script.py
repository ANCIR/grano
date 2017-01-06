# coding: utf-8
from normality import normalize
import csv
import normality
from grano.logic import Loader
rows = ["address", "source", "name", "creation_date"]


if __name__ == "__main__":

    loader = Loader('senegal', project_label='Senegal Companies')
    company = loader.make_entity("Company")


    with open('senegal/senegal-companies.csv', 'r') as csvfile:
        records_reader = csv.reader(csvfile, delimiter=",")
        for row in records_reader:
            for x in range(0, len(rows)):
                #print "%s :: %s" % (rows[x], row[x])
                if row[x]:
                    val = normalize(str(row[x]))
                    company.set( rows[x], val )
            company.save()
        loader.persist()
