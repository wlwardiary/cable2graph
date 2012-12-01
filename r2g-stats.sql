-- from whom did the CIA receive cables over the years
SELECT sndr, COUNT(rcvr) AS c, year(created) AS y 
FROM msg WHERE rcvr = 'RUEAIIA' 
GROUP BY sndr, y HAVING c > 0 ORDER BY y, c;
