## OpenNews Example Graph

This is a simple demo graph representing the OpenNews network of fellows
and news organisations. 

The default loader type is based on ``granoloader``, an independent
Python library that will perform queries against the grano REST API.
Install the library with ``pip``:

    pip install granoloader

You will need to install this package and set the ``GRANO_HOST`` and
``GRANO_APIKEY`` environment variables to your local development install
of grano. You can get the system account's API key with:

    grano adminkey

When the environment variables are set, run ``make``.
