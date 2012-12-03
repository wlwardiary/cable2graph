-- from whom did the CIA receive cables over the years
SELECT 
sndr,
COUNT(DISTINCT(mrn)) AS c, 
YEAR(created) AS y
FROM msg 
WHERE rcvr IN ('RUEAIIA','CIA WASHDC')
GROUP BY sndr, y 
ORDER BY y, c;
