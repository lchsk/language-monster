
all:

check:
	py.test --cov ./ --ignore ./data_loader

send-mail:
	python manage.py send_queued_mail

translations:
	python manage.py makemessages -a

clean-thumbnails:
	python manage.py thumbnail cleanup

beat:
	celery beat -A languagemonster

worker:
	celery worker -A languagemonster

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
