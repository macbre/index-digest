Developer notes
===============

## Testing locally with various version of MySQL

Assume that you want to test `index-digest` locally against MySQL v5.5:

```
docker pull mysql:5.5
sudo service mysql stop
docker run -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -d -p 3306:3306 mysql:5.5
```

Wait for mysql instance to start up. Then from the repository's main directory run:

````
mysql --protocol=tcp -u root -v < setup.sql
./sql/populate.sh
make sql-console
```
