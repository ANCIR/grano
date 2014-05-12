
Installation Guide
==================

These instructions are for making a developer installation of ``grano``. If you want to
set up a production site you'll need to tweak these instructions to run the application
behind a proper web server (e.g. using `gunicorn <http://docs.gunicorn.org/en/latest/>`_).

Before installing ``grano``, make sure you have the following dependencies available on
your system (consider using `Vagrant <http://www.vagrantup.com/>`_ to isolate the
project):

* Python 2.7 and `virtualenv <http://www.virtualenv.org/en/latest/>`_
* Postgres 9.3 or newer
* ElasticSearch 0.9 or newer

When you set up grano, first check out the application from GitHub, create a virtual
environment and install the Python dependencies:

.. code-block:: bash

    git clone https://github.com/pudo/grano.git
    cd grano
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    python setup.py develop 
    bower install
    
If you're unfamiliar with virtualenv, be aware that you will need to execute the 
``source env/bin/activate`` command each time you're working with the project.

Next, you'll need to configure grano. Create a copy of the file
``grano/default_settings.py``, e.g. as ``settings.py`` in the repository base.
Open the file and set up the various account configurations, especially the database
connection string. Make sure you provide an empty Postgres database with UTF-8 set 
as the encoding.
    
Once the new configuration is set up, you need to an environment variables pointing
grano to the configuration file you've created:

.. code-block:: bash

    export GRANO_SETTINGS=`pwd`/settings.py

Once this is done, you can create the database and import schema specifications:

.. code-block:: bash

    grano db upgrade head
    grano schema_import <projectname> <YOUR_MODEL.yaml>

To load the demo project:

.. code-block:: bash

    cd demo/demo_simple
    grano schema_import opennews2 ./model.yaml
    python ./loader.py
    
Finally, you can run grano:

.. code-block:: bash

    grano runserver 
