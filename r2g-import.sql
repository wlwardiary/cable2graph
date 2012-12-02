DROP TABLE IF EXISTS msg;
CREATE TABLE msg (
    mrn char(42),
    sndr char(7),
    rcvr varchar(255),
    created datetime
) CHARSET=utf8;

LOAD DATA INFILE '/tmp/from_to.list'
INTO TABLE msg
CHARACTER SET utf8
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '' 
LINES TERMINATED BY '\n' 
IGNORE 0 LINES 
(mrn, sndr, rcvr, @created)
SET created=FROM_UNIXTIME(@created)
;

ALTER TABLE msg ADD KEY sndr_rcvr (sndr, rcvr);
ALTER TABLE msg ADD KEY created (created);
