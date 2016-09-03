
all: env-dev

check:
	py.test --cov ./

env-dev:
	git checkout master
	python manage.py runserver 8000

env-test:
	git checkout test
	python manage.py runserver 8001

send-mail:
	python manage.py send_queued_mail

lint: \
	lint-api \
	lint-core \
	lint-ctasks \
	lint-management \
	lint-userprofile \
	lint-utility \
	lint-vocabular \

lint-api:
	pylint --load-plugins pylint_django ./api

lint-core:
	pylint --load-plugins pylint_django ./core

lint-ctasks:
	pylint --load-plugins pylint_django ./ctasks

lint-management:
	pylint --load-plugins pylint_django ./management

lint-userprofile:
	pylint --load-plugins pylint_django ./userprofile

lint-utility:
	pylint --load-plugins pylint_django ./utility

lint-vocabulary:
	pylint --load-plugins pylint_django ./vocabulary
