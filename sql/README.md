sql
===

This directory contains `*.sql` files with test schemas. Each reported task / bug should have a separate SQL file with a name `NNNN-short-description.sql` (e.g. `0004-redundant-indices.sql` where 4 is the GitHub's issue number).

Each test schema should be self-contained (e.g. there are no dependencies on other files) and it should be possible to re-apply them, i.e. `DROP TABLE IF EXISTS table-name` statements are there:

### An example

```sql
-- Detect redundant indices
--
-- https://github.com/macbre/index-digest/issues/4
DROP TABLE IF EXISTS `0004-id-foo`;
CREATE TABLE `0004-id-foo` (
        `id` int(9) NOT NULL AUTO_INCREMENT,
        `foo` varbinary(16) NOT NULL DEFAULT '',
        PRIMARY KEY (`id`,`foo`),
        UNIQUE KEY `idx` (`id`,`foo`)
);
-- ...
```
