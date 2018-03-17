# index-digest

[![PyPI](https://img.shields.io/pypi/v/indexdigest.svg)](https://pypi.python.org/pypi/indexdigest)
[![Build Status](https://travis-ci.org/macbre/index-digest.svg?branch=master)](https://travis-ci.org/macbre/index-digest)

Analyses your database queries and schema and suggests indices improvements. You can use `index-digest` as **your database linter**. The goal is to **provide the user with actionable reports** instead of just a list of statistics and schema details. Inspired by [Percona's `pt-index-usage`](https://www.percona.com/doc/percona-toolkit/LATEST/pt-index-usage.html).

`index-digest` does the following:

* it checks the schema of all tables in a given database and suggests improvements (e.g. removal of redundant indices, adding a primary key to ease replication, dropping tables with just a single column or no rows)
* if provided with SQL queries log (via `--sql-log` option) it:
  * checks if all tables, columns and indices are used by these queries
  * reports text columns with character set different than `utf`
  * reports queries that do not use indices
  * reports queries that use filesort, temporary file or full table scan
  * reports queries that are not quite kosher (e.g. `LIKE "%foo%"`, `INSERT IGNORE`, `SELECT *`, `HAVING` clause, high `OFFSET` in pagination queries)
* if run with `--analyze-data` switch it:
  * reports tables with old data (by querying for `MIN()` value of time column) where data retency can be reviewed
  * reports tables with not up-to-date data (by querying for `MAX()` value of time column)

This tool **supports MySQL 5.5, 5.6, 5.7, 8.0 and MariaDB 10.0, 10.2** and runs under **Python 2.7, 3.4, 3.5 and 3.6**.

Results can be reported in a human-readable form, as YAML or sent to syslog and later aggregated & processed using ELK stack.

## Requirements & install

### From `pypi`

```
pip install indexdigest
```

### From git

```
git clone git@github.com:macbre/index-digest.git && cd index-digest
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
  index_digest DSN [--sql-log=<file>] [--format=<formatter>] [--analyze-data] [--checks=<checks> | --skip-checks=<skip-checks>] [--tables=<tables> | --skip-tables=<skip-tables>]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  --format=<formatter>  Use a given results formatter (plain, syslog, yaml)
  --analyze-data    Run additional checks that will query table data (can be slow!)
  --checks=<list>   Comma-separated lists of checks to report
  --skip-checks=<list> Comma-separated lists of checks to skip from report
  --tables=<list>   Comma-separated lists of tables to report
  --skip-tables=<list> Comma-separated lists of tables to skip from report
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://username:password@localhost/dbname
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log
  index_digest mysql://index_digest:qwerty@localhost/index_digest --skip-checks=non_utf_columns
  index_digest mysql://index_digest:qwerty@localhost/index_digest --analyze-data --checks=data_too_old,data_not_updated_recently
  index_digest mysql://index_digest:qwerty@localhost/index_digest --analyze-data --skip-tables=DATABASECHANGELOG,DATABASECHANGELOGLOCK

Visit <https://github.com/macbre/index-digest>
```

## SQL query log

It's a text file with a single SQL query in each line (no line breaks are allowed). Lines that do start with `--` (SQL comment) are ignored. The file can be [generated using `query-digest` when `--sql-log` output mode is selected](https://github.com/macbre/query-digest#output-modes).

An example:

```sql
-- A comment
select * from 0002_not_used_indices order by id
select * from 0002_not_used_indices where foo = 'foo' and id = 2
select count(*) from 0002_not_used_indices where foo = 'foo'
/* foo bar */ select * from 0002_not_used_indices where bar = 'foo'
INSERT  IGNORE INTO `0070_insert_ignore` VALUES ('123', 9, '2017-01-01');
```

## Formatters

`index-digest` can return results in various formats (use `--format` to choose one).

### plain

Emits human-readable report to a console. You can disable colored and bold text by setting env variable `ANSI_COLORS_DISABLED=1`.

### syslog

Pushes JSON-formatted messages via syslog, so they can be aggregated using ELK stack.
Use `SYSLOG_IDENT` env variable to customize syslog's `ident` messages are sent with (defaults to `index-digest`).

```
Dec 28 15:59:58 debian index-digest[17485]: {"meta": {"version": "index-digest v0.1.0", "database_name": "index_digest", "database_host": "debian", "database_version": "MySQL v5.7.20"}, "report": {"type": "redundant_indices", "table": "0004_id_foo", "message": "\"idx\" index can be removed as redundant (covered by \"PRIMARY\")", "context": {"redundant": "UNIQUE KEY idx (id, foo)", "covered_by": "PRIMARY KEY (id, foo)", "schema": "CREATE TABLE `0004_id_foo` (\n  `id` int(9) NOT NULL AUTO_INCREMENT,\n  `foo` varbinary(16) NOT NULL DEFAULT '',\n  PRIMARY KEY (`id`,`foo`),\n  UNIQUE KEY `idx` (`id`,`foo`)\n) ENGINE=InnoDB DEFAULT CHARSET=latin1", "table_data_size_mb": 0.015625, "table_index_size_mb": 0.015625}}}
```

### yaml

Outputs YML file with results and metadata.

## Checks

You can select which checks should be reported by the tool by using `--checks` command line option. Certain checks can also be skipped via `--skip-checks` option. Refer to `index_digest --help` for examples.

> **Number of checks**: 22

* `redundant_indices`: reports indices that are redundant and covered by other
* `non_utf_columns`: reports text columns that have characters encoding set to `latin1` (utf is the way to go)
* `missing_primary_index`: reports tables with no primary or unique key (see [MySQL bug #76252](https://bugs.mysql.com/bug.php?id=76252) and [Wikia/app#9863](https://github.com/Wikia/app/pull/9863))
* `test_tables`: reports tables that seem to be test leftovers (e.g. `some_guy_test_table`)
* `single_column`: reports tables with just a single column
* `empty_tables`: reports tables with no rows
* `generic_primary_key`: reports tables with [a primary key on `id` column](https://github.com/jarulraj/sqlcheck/blob/master/docs/logical/1004.md) (a more meaningful name should be used)
* `use_innodb`: reports table using storage engines different than `InnoDB` (a default for MySQL 5.5+ and MariaDB 10.2+)

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
* `insert_ignore`: reports [queries using `INSERT IGNORE`](https://medium.com/legacy-systems-diary/things-to-avoid-episode-1-insert-ignore-535b4c24406b)
* `select_star`: reports [queries using `SELECT *`](https://github.com/jarulraj/sqlcheck/blob/master/docs/query/3001.md)
* `having_clause`: reports [queries using `HAVING` clause](https://github.com/jarulraj/sqlcheck/blob/master/docs/query/3012.md)
* `high_offset_selects`: report [SELECT queries using high OFFSET](https://www.percona.com/blog/2008/09/24/four-ways-to-optimize-paginated-displays/)

### Additional checks performed on tables data

> You need to use `--analyze-data` command line switch. Please note that these checks will query your tables. **These checks can take a while if queried columns are not indexed**.

* `data_too_old`: reports tables that have really old data, maybe it's worth checking if such long data retention is actually needed (**defaults to three months threshold**, can be customized via `INDEX_DIGEST_DATA_TOO_OLD_THRESHOLD_DAYS` env variable)
* `data_not_updated_recently`: reports tables that were not updated recently, check if it should be up-to-date (**defaults a month threshold**, can be customized via `INDEX_DIGEST_DATA_NOT_UPDATED_RECENTLY_THRESHOLD_DAYS` env variable)

## An example report

```sql
$ index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log sql/0002-not-used-indices-log 
------------------------------------------------------------
Found 85 issue(s) to report for "index_digest" database
------------------------------------------------------------
MySQL v5.7.21 at debian
index-digest v1.0.0
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
missing_primary_index → table affected: 0034_querycache

✗ "0034_querycache" table does not have any primary or unique index

  - schema: CREATE TABLE `0034_querycache` (
      `qc_type` varbinary(32) NOT NULL,
      `qc_value` int(10) unsigned NOT NULL DEFAULT '0',
      `qc_namespace` int(11) NOT NULL DEFAULT '0',
      `qc_title` varchar(255) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL DEFAULT '',
      KEY `qc_type` (`qc_type`,`qc_value`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8

------------------------------------------------------------
test_tables → table affected: 0075_some_guy_test_table

✗ "0075_some_guy_test_table" seems to be a test table

  - schema: CREATE TABLE `0075_some_guy_test_table` (
      `id` int(9) NOT NULL AUTO_INCREMENT,
      `name` varchar(255) NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8

------------------------------------------------------------
single_column → table affected: 0074_bag_of_ints

✗ "0074_bag_of_ints" has just a single column

  - schema: CREATE TABLE `0074_bag_of_ints` (
      `id` int(9) NOT NULL AUTO_INCREMENT,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8

------------------------------------------------------------
empty_tables → table affected: 0089_empty_table

✗ "0089_empty_table" table has no rows, is it really needed?

  - schema: CREATE TABLE `0089_empty_table` (
      `id` int(9) NOT NULL AUTO_INCREMENT,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1

------------------------------------------------------------
generic_primary_key → table affected: 0094_generic_primary_key

✗ "0094_generic_primary_key" has a primary key called id, use a more meaningful name

  - schema: CREATE TABLE `0094_generic_primary_key` (
      `id` int(9) NOT NULL AUTO_INCREMENT,
      `foo` varchar(16) NOT NULL DEFAULT '',
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1

------------------------------------------------------------
use_innodb → table affected: 0036_use_innodb_myisam

✗ "0036_use_innodb_myisam" uses MyISAM storage engine

  - schema: CREATE TABLE `0036_use_innodb_myisam` (
      `item_id` int(9) NOT NULL AUTO_INCREMENT,
      `foo` int(8) DEFAULT NULL,
      PRIMARY KEY (`item_id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=latin1
  - engine: MyISAM

------------------------------------------------------------
not_used_indices → table affected: 0002_not_used_indices

✗ "test_id_idx" index was not used by provided queries

  - not_used_index: KEY test_id_idx (test, id)

------------------------------------------------------------
not_used_tables → table affected: 0020_big_table

✗ "0020_big_table" table was not used by provided queries

  - schema: CREATE TABLE `0020_big_table` (
      `id` int(9) NOT NULL AUTO_INCREMENT,
      `val` int(9) NOT NULL,
      `text` char(5) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `text_idx` (`text`)
    ) ENGINE=InnoDB AUTO_INCREMENT=100001 DEFAULT CHARSET=utf8
  - table_size_mb: 5.03125
  - rows_estimated: 100405

------------------------------------------------------------
insert_ignore → table affected: 0070_insert_ignore

✗ "INSERT IGNORE INTO `0070_insert_ignore` VALUES (9,..." query uses a risky INSERT IGNORE

  - query: INSERT IGNORE INTO `0070_insert_ignore` VALUES (9, '123', '2017-01-01');
  - schema: CREATE TABLE `0070_insert_ignore` (
      `id` int(9) NOT NULL,
      `text` char(5) NOT NULL,
      `time` datetime DEFAULT NULL,
      UNIQUE KEY `id` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8

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

------------------------------------------------------------
select_star → table affected: bar

✗ "SELECT t.* FROM bar AS t" query uses SELECT *

  - query: SELECT t.* FROM bar AS t;

------------------------------------------------------------
having_clause → table affected: sales

✗ "SELECT s.cust_id,count(s.cust_id) FROM SH.sales s ..." query uses HAVING clause

  - query: SELECT s.cust_id,count(s.cust_id) FROM SH.sales s GROUP BY s.cust_id HAVING s.cust_id != '1660' AND s.cust_id != '2'

(...)

------------------------------------------------------------
data_too_old → table affected: 0028_data_too_old

✗ "0028_data_too_old" has rows added 184 days ago, consider changing retention policy

  - diff_days: 184
  - data_since: 2017-08-17 12:03:44
  - data_until: 2018-02-17 12:03:44
  - date_column_name: timestamp
  - schema: CREATE TABLE `0028_data_too_old` (
      `item_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
      `cnt` int(8) unsigned NOT NULL,
      `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`item_id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1
  - rows: 4
  - table_size_mb: 0.015625

------------------------------------------------------------
data_not_updated_recently → table affected: 0028_data_not_updated_recently

✗ "0028_data_not_updated_recently" has the latest row added 40 days ago, consider checking if it should be up-to-date

  - diff_days: 40
  - data_since: 2017-12-29 12:03:44
  - data_until: 2018-01-08 12:03:44
  - date_column_name: timestamp
  - schema: CREATE TABLE `0028_data_not_updated_recently` (
      `item_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
      `cnt` int(8) unsigned NOT NULL,
      `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`item_id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1
  - rows: 3
  - table_size_mb: 0.015625

------------------------------------------------------------
high_offset_selects → table affected: page

✗ "SELECT /* CategoryPaginationViewer::processSection..." query uses too high offset impacting the performance

  - query: SELECT /* CategoryPaginationViewer::processSection */  page_namespace,page_title,page_len,page_is_redirect,cl_sortkey_prefix  FROM `page` INNER JOIN `categorylinks` FORCE INDEX (cl_sortkey) ON ((cl_from = page_id))  WHERE cl_type = 'page' AND cl_to = 'Spotify/Song'  ORDER BY cl_sortkey LIMIT 927600,200
  - limit: 200
  - offset: 927600

------------------------------------------------------------
Queries performed: 100
```

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
