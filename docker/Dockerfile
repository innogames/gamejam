FROM python:2

# Installing WiringPi Library Package
RUN apt-get update && \
    apt-get install --no-install-recommends -yq \
    build-essential \
    virtualenv git

WORKDIR /usr/src/myapp

RUN rm -rf env
RUN pip install --no-cache-dir virtualenv2
#RUN virtualenv env

#RUN pip install --no-cache-dir tornado
#RUN pip install --no-cache-dir flask
#RUN pip install --no-cache-dir flask-mail
#RUN pip install --no-cache-dir flask-sqlalchemy
#RUN pip install --no-cache-dir flask-wtf
#RUN pip install --no-cache-dir flask-login
#RUN pip install --no-cache-dir flask-markdown
#RUN pip install --no-cache-dir python-dateutil
#RUN pip install --no-cache-dir scrypt
#RUN pip install --no-cache-dir requests
#RUN pip install --no-cache-dir alembic
#RUN pip install --no-cache-dir flask-principal
#RUN pip install --no-cache-dir flask-cache
#RUN pip install --no-cache-dir python-memcached
#RUN pip install --no-cache-dir psycopg2
#RUN pip install --no-cache-dir pyfscache
#RUN pip install --no-cache-dir flask-caching
#RUN pip install --no-cache-dir python-wordpress-xmlrpc
#RUN pip install --no-cache-dir beautifulsoup4
#RUN pip install MySQL-python

RUN ln -s /usr/local/bin/virtualenv /usr/local/bin/virtualenv2

# Initializing system
ENV INITSYSTEM on

#CMD make -C /usr/src/myapp run-dev
CMD sh run-dev.sh
