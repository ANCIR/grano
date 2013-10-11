
Steps: 
  * Make a UI mockup to see how this would look: 
    * Entity view page 
    * Fragment view 
    * Fragment editing 
    * Menus, footer etc. 
  * Write down lots of stuff:
    * About narrative vs. structured SNA
    * Example queries, what do the advanced screens look like?
  * Select a sample story:
    * NSU/right-wing terrorism in Germany
    * Snowden/NSA story
    * Jacqui's idea

Use this: 
  * BrowserID / Persona - https://github.com/garbados/flask-browserid
  * Wikipedia page titles data list?

What is the minimal product?
  * Create a fragment 
  * Edit a fragment 
  * Edit an entity (title, description, tagline)
  * List fragments for one entity

Next version features
  * Global timeline, faceting feature
  * "Follow" feature for entities


Domain Model
============

User
  email
  display_name

Project
  slug
  label
  description

ProjectMember 
  email
  role
  project

Entity
  project
  label
  tagline
  description
  project
  creator

Fragment
  text
  time_from
  time_until
  source_url
  source_label





