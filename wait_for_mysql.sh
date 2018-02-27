#!/bin/bash
# wait for MySQL server to be fully set up
echo -n 'Waiting for MySQL server '

until mysql --silent --protocol=tcp -uroot -e 'select 1' 1>/dev/null 2>/dev/null
do
	echo -n '.'
	sleep 1
done

echo ' done'
