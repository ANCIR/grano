
API documentation
=================

``grano`` will eventually feature two separate application programming 
interfaces: a Python-based API for bulk data loading and interacting with 
the internals of the application; and a RESTful web API that will allow 
interacting with the graph from web clients, e.g. directly through the
browser.

Further, the following questions are open at the moment:

* Do we really want a Python loader API, or rather support a packaged 
  file format for bulk loading (e.g. zipped JSON)?
* Does ``grano`` handle its own authentication, delegate to specific 
  OAUth providers or generic providers like Twitter, GitHub or
  Facebook?

