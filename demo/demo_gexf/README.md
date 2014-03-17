# Importing from a GEXF file

This is a quick demonstration on how to import a graph from a [GEXF](http://gexf.net/format/) file.

The data comes from [Stanford's Digital Humanities](https://dhs.stanford.edu/gephi-workshop/sample-graph-data/) site.

## How to run:

  - Download the GEXF data from: https://dhs.stanford.edu/dh/gephi/dh11.gexf
  - Import the schemata: `grano schema_import dhs_stanford model.yaml`
  - Run the loader: `python loader.py`
