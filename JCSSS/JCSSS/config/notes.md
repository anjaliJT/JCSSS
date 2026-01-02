How You Run Each Environment
- Local
export DJANGO_SETTINGS_MODULE=JCSSS.config.dev
python manage.py runserver 

- AWS / Production
export DJANGO_SETTINGS_MODULE=JCSSS.config.prod
gunicorn JCSSS.wsgi:application

# What You GAIN From This Refactor

✔ No accidental prod misconfig
✔ Clean AWS S3 setup
✔ Easy debugging
✔ Future staging ready
✔ Professional-grade Django structure

python manage.py products --file jf2-1.csv
python manage.py products --file jm-1.csv