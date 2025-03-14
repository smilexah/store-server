# Store Server

The project for study Django.

#### Stack:

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Celery](https://docs.celeryq.dev/en/stable/)

1. ```
   python.exe -m pip install --upgrade pip
   ```

## Local Developing
   
1. Run project dependencies, migrations, fill the database with the fixture data etc.:
   ```bash
   python manage.py migrate
   python manage.py loaddata <path_to_fixture_files>
   python manage.py runserver 
   ```
   
2. Run [Redis Server](https://redis.io/docs/getting-started/installation/):
   ```bash
   redis-server
   ```
   
3. Run Celery:
   ```bash
   celery -A store worker --loglevel=INFO
   ```
   or
   ```bash
   celery -A store worker --loglevel=DEBUG --pool=solo
   ```
