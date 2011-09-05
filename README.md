# cables.csv to graph to svg

the short version

create list of IDs and edges as plain text files

    $ python ref.py cables.csv

read and modify c2g.py, then create any.gml
    
    $ python c2g.py

create html with inline svg

    $ python gml2svg.py any.gml > any.html

# note

* dont run ref.py, the code already has all the files you need.
* c2g.py reads calccache and graphcache, so you dont have to calculate
  the graph weight again. Can take 10-15min if you remove the cache.
* change svg.tmpl to customize the output

# copyleft

GPL fkn a 3

# contact

need help? ask!

https://twitter.com/c2graph

