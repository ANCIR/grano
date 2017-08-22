FROM granoproject/base:latest

# Node dependencies
RUN npm --quiet --silent install -g bower uglify-js less

COPY . /grano
WORKDIR /grano
RUN python setup.py -qq install

CMD gunicorn -w 3 -t 1800 grano.manage:app
