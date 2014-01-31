
Installation Guide
==================

These instructions are for making a developer installation of ``grano``. If you want to
set up a production site you'll need to tweak these instructions to run the application
behind a proper web server (e.g. using `gunicorn <http://docs.gunicorn.org/en/latest/>`_).

Before installing ``grano``, make sure you have the following dependencies available on
your system (consider using `Vagrant <http://www.vagrantup.com/>`_ to isolate the
project):

* Python 2.7 and `virtualenv <http://www.virtualenv.org/en/latest/>`_
* Twitter's `bower <https://github.com/bower/bower>`_ for installing JS dependencies.
* `UglifyJS <https://github.com/mishoo/UglifyJS/>`_ for JS minification.

When you set up grano, first check out the application from GitHub, create a virtual
environment and install the Python dependencies::

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
Open the file and set up the various account configurations.
    
Once the new configuration is set up, you need to an environment variables pointing
grano to the configuration file you've created::

    export GRANO_SETTINGS=`pwd`/settings.py

Once this is done, you can create the database and import schema specifications::

    python grano/manage.py createdb
    python grano/manage.py schema_import <YOUR_MODEL.yaml>
    
Finally, you can run grano::

    python grano/manage.py runserver 

