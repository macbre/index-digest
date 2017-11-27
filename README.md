# index-digest

[![Build Status](https://travis-ci.org/macbre/index-digest.svg?branch=master)](https://travis-ci.org/macbre/index-digest)

Analyses your database queries and schema and suggests indices improvements. You can use `index-digest` as **your database linter**. The goal is to **provide the user with actionable reports** instead of just a list of statistics and schema details. Inspired by [Percona's `pt-index-usage`](https://www.percona.com/doc/percona-toolkit/LATEST/pt-index-usage.html).

`index-digest` does the following:

* it checks the schema of all tables in a given database and suggests improvements (e.g. removal of redundant indices)
* if provided with SQL queries log (via `--sql-log` option) it:
  * checks if all tables, columns and indices are used by these queries
  * reports text columns with character set different than `utf`
  * reports queries that do not use indices
  * reports queries that use filesort, temporary file or full table scan

This tool **supports MySQL 5.5, 5.6, 5.7, 8.0 and MariaDB 10.0, 10.2** .

## Requirements & install

```
sudo apt-get install libmysqlclient-dev python-dev virtualenv

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
  index_digest mysql://username:password@localhost/dbname
  index_digest mysql://index_digest:qwerty@localhost/index_digest
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log

Visit <https://github.com/macbre/index-digest>
```

## An example

```
$ index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log sql/0002-not-used-indices-log 
------------------------------------------------------------
Found 15 issue(s) to report for "index_digest" database
------------------------------------------------------------
MySQL v5.5.58-0+deb8u1 at debian
index-digest v0.1.0
------------------------------------------------------------
redundant_indices → table affected: 0004_id_foo

✗ "idx" index can be removed as redundant (covered by "PRIMARY")

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
redundant_indices → table affected: 0004_id_foo_bar

✗ "idx_foo" index can be removed as redundant (covered by "idx_foo_bar")

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
not_used_indices → table affected: 0002_not_used_indices

✗ "test_id_idx" index was not used by provided queries

  - not_used_index: KEY test_id_idx (test, id)

------------------------------------------------------------
not_used_tables → table affected: 0000_the_table

✗ "0000_the_table" table was not used by provided queries

------------------------------------------------------------
non_utf_columns → table affected: 0032_latin1_table

✗ "name" text column has "latin1" character set defined

  - column: name
  - column_character_set: latin1
  - column_collation: latin1_swedish_ci

------------------------------------------------------------

(...)

------------------------------------------------------------
queries_using_filesort → table affected: 0020_big_table

✗ "SELECT val, count(*) FROM 0020_big_table WHERE id ..." query used filesort

  - query: SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val
  - explain_extra: Using where; Using temporary; Using filesort
  - explain_rows: 11
  - explain_filtered: None
  - explain_key: PRIMARY

------------------------------------------------------------
queries_using_temporary → table affected: 0020_big_table

✗ "SELECT val, count(*) FROM 0020_big_table WHERE id ..." query used temporary

  - query: SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val
  - explain_extra: Using where; Using temporary; Using filesort
  - explain_rows: 11
  - explain_filtered: None
  - explain_key: PRIMARY

------------------------------------------------------------
queries_using_full_table_scan → table affected: 0020_big_table

✗ "SELECT * FROM 0020_big_table" query triggered full table scan

  - query: SELECT * FROM 0020_big_table
  - explain_rows: 9041

------------------------------------------------------------
selects_with_like → table affected: 0020_big_table

✗ "SELECT * FROM 0020_big_table WHERE text LIKE '%00'" query uses LIKE with left-most wildcard

  - query: SELECT * FROM 0020_big_table WHERE text LIKE '%00'
  - explain_extra: Using where
  - explain_rows: 100623
```

## SQL query log

It's a text file with a single SQL query in each line (no line breaks are allowed). Lines that do not start with `SELECT` are ignored. The file can be [generated using `query-digest` when `--sql-log` output mode is selected](https://github.com/macbre/query-digest#output-modes).

An example:

```sql
-- A comment
select * from 0002_not_used_indices order by id
select * from 0002_not_used_indices where foo = 'foo' and id = 2
select count(*) from 0002_not_used_indices where foo = 'foo'
select * from 0002_not_used_indices where bar = 'foo'
```

## Checks

* `redundant_indices`: reports indices that are redundant and covered by other
* `non_utf_columns`: reports text columns that have characters encoding set to `latin1` (utf is the way to go)

### Additional checks performed on SQL log

> You need to provide SQL log file via `--sql-log` option

* `not_used_columns`: checks which columns were not used by SELECT queries
* `not_used_indices`: checks which indices are not used by SELECT queries
* `not_used_tables`: checks which tables are not used by SELECT queries
* `queries_not_using_index`: reports SELECT queries that do not use any index
* `queries_using_filesort`: reports SELECT queries that require filesort ([a sort can’t be performed from an index and quicksort is used](https://www.percona.com/blog/2009/03/05/what-does-using-filesort-mean-in-mysql/))
* `queries_using_temporary`: reports SELECT queries that require a temporary table to hold the result
* `queries_using_full_table_scan`: reports SELECT queries that require a [full table scan](https://dev.mysql.com/doc/refman/5.7/en/table-scan-avoidance.html)
* `selects_with_like`: reports SELECT queries that use `LIKE '%foo'` conditions (they can not use an index)

## Success stories

> Want to add your entry here? Submit a pull request

* By running `index-digest` at [Wikia](http://wikia.com) on shared database clusters (including tables storing ~450 mm of rows with 300+ GiB of data) we were able to [reclaim around 1.25 TiB of MySQL storage space across all replicas](https://medium.com/legacy-systems-diary/linting-your-database-schema-cd8947835a52).

## Read more

* [Percona Database Performance Blog](https://www.percona.com/blog/)
* [High Performance MySQL, 3rd Edition by Vadim Tkachenko, Peter Zaitsev, Baron Schwartz](https://www.safaribooksonline.com/library/view/high-performance-mysql/9781449332471/ch05.html)
* [Percona | Indexing 101: Optimizing MySQL queries on a single table](https://www.percona.com/blog/2015/04/27/indexing-101-optimizing-mysql-queries-on-a-single-table/)
* [Percona | `pt-index-usage`](https://www.percona.com/doc/percona-toolkit/LATEST/pt-index-usage.html) / [find unused indexes](https://www.percona.com/blog/2012/06/30/find-unused-indexes/)

### Slides

* [Percona | MySQL Indexing: Best Practices](https://www.percona.com/files/presentations/WEBINAR-MySQL-Indexing-Best-Practices.pdf)
