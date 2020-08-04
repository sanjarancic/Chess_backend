
### Starting postgres service
`brew services start postgresql`


### Creating database (once)
`createdb chess`

### Adding user (once)
`psql chess`

`CREATE USER chess WITH PASSWORD 'chess';`

### Initialize migrations (once)
`python manage.py db init`

### Running migrations
`python manage.py db migrate`

### Apply migrations
`python manage.py db upgrade`