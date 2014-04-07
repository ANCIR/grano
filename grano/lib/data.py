from unicodecsv import DictReader, DictWriter


class CSVImporter(object):
    """ A CSV-backed resource with the datas in it. """ 
    
    def __init__(self, fh):
        self.reader = DictReader(fh)
        self.data = list(self.reader)

    @property
    def headers(self):
        headers = set()
        for row in self.data:
            headers = headers.union(row.keys())
        return headers

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

