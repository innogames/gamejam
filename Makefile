default: run

setup:
	virtualenv3 -p python3 env && . env/bin/activate && \
		pip install --upgrade \
			flask flask-mail flask-sqlalchemy flask-wtf \
			flask-login flask-uploads Flask-Caching Flask-Markdown python-dateutil \
			scrypt requests alembic flask-principal \
			flask-cache python-memcached psycopg2 python-wordpress-xmlrpc \
			BeautifulSoup4 tornado pymysql email_validator gunicorn raven[flask]

run-prod:
	. env/bin/activate && gunicorn -w 10 -b 127.0.0.1:5000 flamejam:app

run:
	. env/bin/activate && python3 runserver.py

run-dev:
	. env/bin/activate && python3 runserver-dev.py

init-db:
	. env/bin/activate && python3 scripts/init-db.py

seed-db:
	. env/bin/activate && python3 scripts/seed-db.py

install:
	mkdir -p $(DESTDIR)/srv/flamejam
	cp -r alembic flamejam scripts $(DESTDIR)/srv/flamejam
	cp alembic.ini flamejam.wsgi runserver.py Makefile $(DESTDIR)/srv/flamejam/

	mkdir -p $(DESTDIR)/etc/flamejam

	mkdir -p $(DESTDIR)/usr/share/doc/flamejam
	cp -r doc/* $(DESTDIR)/usr/share/doc/flamejam/
	cp LICENSE README.md $(DESTDIR)/usr/share/doc/flamejam/

	cd $(DESTDIR)/srv/flamejam && make setup

uninstall:
	rm -r $(DESTDIR)/srv/flamejam
	rm -r $(DESTDIR)/etc/flamejam
	rm -r $(DESTDIR)/usr/share/doc/flamejam
