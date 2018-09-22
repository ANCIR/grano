FROM python:2.7.15
MAINTAINER Code for Africa <support@codeforafrica.org>
ENV DEBIAN_FRONTEND noninteractive

# Setup Node.js
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get -q install -y nodejs

# Upgrade what we can
RUN pip install -q --upgrade pip && pip install -q --upgrade setuptools
