-- create databases
CREATE DATABASE IF NOT EXISTS index_digest;
CREATE DATABASE IF NOT EXISTS index_digest_empty; -- #146

-- create a user and grant access to our databases
CREATE USER 'index_digest'@'%' IDENTIFIED BY 'qwerty';

GRANT ALL ON index_digest.* TO 'index_digest'@'%';
GRANT ALL ON index_digest_empty.* TO 'index_digest'@'%';
