# Test flask application

- Use **pipenv install** to install dependencies.
- Use **pipenv lock -r > requirements.txt** to create requirements.txt file for container.

- Create database flask_test

- flask db init
- flask db migrate
- flask db upgrade

## Environment variables

- POSTGRES_PASSWORD=password
- FLASK_DB=db
- FLASK_CONFIG=development
- FLASK_APP=run.py
- FLASK_DB=postgres://postgres:password@host:5432/db
