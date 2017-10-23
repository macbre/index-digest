# index-digest

[![Build Status](https://travis-ci.org/macbre/index-digest.svg?branch=master)](https://travis-ci.org/macbre/index-digest)

Analyses your database queries and schema and suggests indices improvements. You can use `index-digest` as your database linter.

`index-digest` does the following:

* it checks the schema of all tables in a given database and suggests improvements (e.g. removal of redundant indices)
* if provided with SQL queries log (via `--sql-log` option) it:
  * checks if all tables, columns and indices are used by these queries
  * reports queries that do not use indices
  * reports queries that use filesort or temporary file

This tool **supports MySQL 5.5, 5.6 and 5.7**.

## Requirements & install

```
sudo apt-get install libmysqlclient-dev python-dev

virtualenv env
source env/bin/activate
make install
```

## How to run it?

```
$ index_digest -h
index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN [--sql-log=<file>]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://index_digest:qwerty@localhost/index_digest
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log

Visit <https://github.com/macbre/index-digest>
```

## An example

```
$ index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log sql/0002-not-used-indices-log 
Query <select * from 0002_not_used_indices where bar = 'foo'> does not use any index on `0002_not_used_indices` table
------------------------------------------------------------
Found 12 issue(s) to report for "index_digest" database
------------------------------------------------------------
redundant_indices / 0004_id_foo

	"idx" index can be removed as redundant (covered by "PRIMARY")

	- redundant: UNIQUE KEY idx (id, foo)
	- covered_by: PRIMARY KEY (id, foo)
	- schema: CREATE TABLE `0004_id_foo` (
	    `id` int(9) NOT NULL AUTO_INCREMENT,
	    `foo` varbinary(16) NOT NULL DEFAULT '',
	    PRIMARY KEY (`id`,`foo`),
	    UNIQUE KEY `idx` (`id`,`foo`)
	  ) ENGINE=InnoDB DEFAULT CHARSET=latin1
	- table_data_size_mb: 0.015625
	- table_index_size_mb: 0.015625

------------------------------------------------------------
redundant_indices / 0004_id_foo_bar

	"idx_foo" index can be removed as redundant (covered by "idx_foo_bar")

	- redundant: KEY idx_foo (foo)
	- covered_by: KEY idx_foo_bar (foo, bar)
	- schema: CREATE TABLE `0004_id_foo_bar` (
	    `id` int(9) NOT NULL AUTO_INCREMENT,
	    `foo` varbinary(16) NOT NULL DEFAULT '',
	    `bar` varbinary(16) NOT NULL DEFAULT '',
	    PRIMARY KEY (`id`),
	    KEY `idx_foo` (`foo`),
	    KEY `idx_foo_bar` (`foo`,`bar`),
	    KEY `idx_id_foo` (`id`,`foo`)
	  ) ENGINE=InnoDB DEFAULT CHARSET=latin1
	- table_data_size_mb: 0.015625
	- table_index_size_mb: 0.046875

------------------------------------------------------------
not_used_indices / 0002_not_used_indices

	"test_id_idx" index was not used by provided queries

	- not_used_index: KEY test_id_idx (test, id)

------------------------------------------------------------
not_used_tables / 0000_the_table

	"0000_the_table" table was not used by provided queries

------------------------------------------------------------
not_used_tables / 0004_id_foo

	"0004_id_foo" table was not used by provided queries

------------------------------------------------------------
not_used_tables / 0004_id_foo_bar

	"0004_id_foo_bar" table was not used by provided queries

------------------------------------------------------------
not_used_tables / 0006_not_used_columns

	"0006_not_used_columns" table was not used by provided queries

------------------------------------------------------------
not_used_tables / 0006_not_used_tables

	"0006_not_used_tables" table was not used by provided queries

------------------------------------------------------------
not_used_columns / 0002_not_used_indices

	"id" column was not used by provided queries

	- column_type: int
	- column_name: id

------------------------------------------------------------
not_used_columns / 0002_not_used_indices

	"foo" column was not used by provided queries

	- column_type: varchar
	- column_name: foo

------------------------------------------------------------
not_used_columns / 0002_not_used_indices

	"test" column was not used by provided queries

	- column_type: varchar
	- column_name: test

------------------------------------------------------------
not_used_columns / 0002_not_used_indices

	"bar" column was not used by provided queries

	- column_type: varchar
	- column_name: bar

------------------------------------------------------------
```

## Checks

* `not_used_columns`: using provided SQL log file (via `--sql-log`) checks which columns were not used by SELECT queries
* `not_used_indices`: using provided SQL log file (via `--sql-log`) checks which indices are not used by SELECT queries
* `not_used_tables`: using provided SQL log file (via `--sql-log`) checks which tables are not used by SELECT queries
* `redundant_indices`: reports indices that are redundant and covered by other

## Read more

* [High Performance MySQL, 3rd Edition by Vadim Tkachenko, Peter Zaitsev, Baron Schwartz](https://www.safaribooksonline.com/library/view/high-performance-mysql/9781449332471/ch05.html)
* [Percona | Indexing 101: Optimizing MySQL queries on a single table](https://www.percona.com/blog/2015/04/27/indexing-101-optimizing-mysql-queries-on-a-single-table/)
* [Percona | `pt-index-usage`](https://www.percona.com/doc/percona-toolkit/LATEST/pt-index-usage.html) / [find unused indexes](https://www.percona.com/blog/2012/06/30/find-unused-indexes/)

### Slides

* [Percona | MySQL Indexing: Best Practices](https://www.percona.com/files/presentations/WEBINAR-MySQL-Indexing-Best-Practices.pdf)
