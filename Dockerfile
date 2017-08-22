FROM granoproject/base:latest

# Node dependencies
RUN npm --quiet --silent install -g bower uglifyjs

COPY . /grano
WORKDIR /grano
RUN python setup.py install

CMD gunicorn -w 3 -t 1800 grano.manage:app
