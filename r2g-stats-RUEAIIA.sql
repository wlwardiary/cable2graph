-- from whom did the CIA receive how many cables?
SELECT 
sndr, 
COUNT(DISTINCT(mrn)) AS c 
FROM msg 
WHERE rcvr IN ('RUEAIIA') 
GROUP BY sndr 
ORDER BY c;

-- from whom did the CIA receive how many cables over the years?
SELECT 
sndr,
COUNT(DISTINCT(mrn)) AS c, 
YEAR(created) AS y
FROM msg 
WHERE rcvr IN ('RUEAIIA')
GROUP BY sndr, y 
ORDER BY y, c;

-- from whom did the CIA receive more then 30 cables each month?
SELECT 
sndr,
COUNT(DISTINCT(mrn)) AS c, 
YEAR(created) AS y,
MONTH(created) AS m
FROM msg 
WHERE rcvr IN ('RUEAIIA')
GROUP BY sndr, y, m
HAVING c > 30
ORDER BY y, m, c;

