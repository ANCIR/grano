# Installing grano

These instructions are for making a developer installation of grano. If you want to
set up a production site you'll need to tweak these instructions to run grano behind
a proper web server.

Before installing grano, make sure you have the following dependencies available on
your system (consider using [Vagrant](http://www.vagrantup.com/) to isolate the
project):

* Python 2.7 and [virtualenv](http://www.virtualenv.org/en/latest/)
* Twitter's [bower](https://github.com/bower/bower) for installing JS dependencies.
* [UglifyJS](https://github.com/mishoo/UglifyJS/)

When you set up grano, first check out the application from GitHub, create a virtual
environment and install the Python dependencies:

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
grano to the configuration file you've created. 

    export GRANO_SETTINGS=`pwd`/settings.py
    
Finally, you can run grano:

    python grano/manage.py runserver 

