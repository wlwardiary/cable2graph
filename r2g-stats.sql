-- from whom did the CIA receive cables over the years
SELECT sndr, COUNT(rcvr) AS c, YEAR(created) AS y 
FROM msg WHERE rcvr = 'RUEAIIA' 
GROUP BY sndr, y ORDER BY y, c;
