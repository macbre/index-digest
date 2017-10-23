# index-digest

[![Build Status](https://travis-ci.org/macbre/index-digest.svg?branch=master)](https://travis-ci.org/macbre/index-digest)

Analyses your database queries and schema and suggests indices improvements. You can use `index-digest` as your database linter.

`index-digest` does the following:

* it checks the schema of all tables in a given database and suggests improvements (e.g. removal of redundant indices)
* if provided with SQL queries log (via `--sql-log` option) it:
  * checks if all tables, columns and indices are used by these queries
  * reports queries that do not use indices
  * reports queries that use filesort or temporary file

## Requirements

```
sudo apt-get install libmysqlclient-dev
```

## An example

```
$ make demo
index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log sql/0006-not-used-columns-and-tables-log
------------------------------------------------------------------------------------------------------------------------
Found 6 issue(s) to report for "index_digest" database
------------------------------------------------------------------------------------------------------------------------
redundant_indices / 0004_id_foo

	UNIQUE KEY idx (id, foo) index can be removed as redundant (covered by PRIMARY KEY (id, foo))

	{
	 "redundant": "UNIQUE KEY idx (id, foo)",
	 "covered_by": "PRIMARY KEY (id, foo)"
	}
------------------------------------------------------------------------------------------------------------------------
redundant_indices / 0004_id_foo_bar

	KEY idx_foo (foo) index can be removed as redundant (covered by KEY idx_foo_bar (foo, bar))

	{
	 "redundant": "KEY idx_foo (foo)",
	 "covered_by": "KEY idx_foo_bar (foo, bar)"
	}
------------------------------------------------------------------------------------------------------------------------
...
------------------------------------------------------------------------------------------------------------------------
not_used_tables / 0006_not_used_tables

	Table was not used by provided queries

	n/a
------------------------------------------------------------------------------------------------------------------------
not_used_columns / 0006_not_used_columns

	bar column was not used by provided queries

	{
	 "column_type": "varchar",
	 "column_name": "bar"
	}
------------------------------------------------------------------------------------------------------------------------
...
------------------------------------------------------------------------------------------------------------------------
not_used_indices / 0002_not_used_indices

	"KEY test_id_idx (test, id)" was not used by provided queries

	- not_used_index: KEY test_id_idx (test, id)
------------------------------------------------------------------------------------------------------------------------
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
