# Grano

It's like Facebook, but for terrorists!

Grano will track connections between people, companies and organisations through textual summaries of their interactions. 

### Who is this for?

Grano is intended to be easily deployable within news organisations, so that it can be used by reporters in investigative projects (or across a series of investigative efforts). 

### How is this different from existing projects?

Grano focusses on creating an environment for reporters to manage pieces of evidence in a structured way, while providing and API to render these into interactive features or visualizations. 

### Give me an example!

We'll be using Markdown for the fragments. It might look like this:

	On {May 20, 2013}, [[NSA]] contractor [[Edward Snowden]] flew to @{Hong Kong} to meet 
	with [[Glenn Greenwald]] and [[Laura Poitras]] to leak documents about the Agency's 
	secret surveillance programmes.
	
Additionally, a reporter can specify structured context, such as a source URL, begin and end dates or (in later development stages) more structured information on the relationships that are described in the fragment. 

## Domain Model

What are our domain objects?

* **Project** - a partitioned section of the other entities with a specific purpose.
* **Entity** - a thing; such as a person, company or other organisation.
* **Fragment** - a piece of text; annotated with references to various entities. 
* **Reference** - information stored to connect an entity and a fragment.

In essence, there will be two types of entities: proper entites for people, orgs etc. and implicit entities for times and places. In later stages, Grano may have the **Relationship** domain object common for SNA tools, but for now **Fragments** are a narrative (i.e. humanly typed) replacement for them.

## Existing Projects

This project is heavily inspired by [Hypernotes](http://github.com/okfn/hypernotes), [Poderopedia](http://poderopedia.org), [Connected China](http://connectedchina.reuters.com) and [LittleSis](http://littlesis.org). Other related projects include [Mapa74](http://mapa76.info), [PopIt](https://github.com/mysociety/popit) (and the [Popolo specification](http://popoloproject.com/)), [InfluenceNetworks](http://owni.eu/2011/04/11/influence-networks-the-six-degrees-of-investigative-journalism/), [TheyRule](http://www.theyrule.net/), [Gephi](http://gephi.org) (and [sigma.js](http://sigmajs.org)), [MIT Immersion](https://immersion.media.mit.edu/) and even the [i2 Analysts Notebook](http://www-03.ibm.com/software/products/de/de/analysts-notebook/).

Here's a secret Google group about this: [https://groups.google.com/forum/#!forum/sna-for-journalists](https://groups.google.com/forum/#!forum/sna-for-journalists).