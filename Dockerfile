FROM granoproject/base:latest

# Node dependencies
RUN npm --quiet --silent install -g bower uglifyjs

# Run the install
COPY requirements.txt /tmp/
RUN pip install -q -r /tmp/requirements.txt

COPY . /grano
WORKDIR /grano
RUN pip install -q -e .

CMD gunicorn -w 3 -t 1800 grano.manage:app
