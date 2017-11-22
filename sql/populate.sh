#!/bin/bash
# This script is used to populate the MySQL instance with the content of all SQL files in this directory
FILES=`ls sql/*.sql`

for FILE in $FILES
do
	echo -n "* Importing ${FILE} ... "
	cat $FILE | mysql --protocol=tcp -uindex_digest -pqwerty index_digest
	echo "done"
done
