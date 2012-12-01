DROP TABLE IF EXISTS msg;
CREATE TABLE msg (
    mrn varchar(255),
    sndr varchar(255),
    rcvr varchar(255),
    created datetime
) ENGINE=InnoDB CHARSET=utf8;

LOAD DATA INFILE '/tmp/from_to.list'
INTO TABLE msg
CHARACTER SET utf8
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '' 
LINES TERMINATED BY '\n' 
IGNORE 0 LINES 
(mrn, sndr, rcvr, @created)
SET created=FROM_UNIXTIME(@created)
;
