# cables.csv to graph to svg

the short version

create list of IDs and edges as plain text files

    $ python ref.py cables.csv (optional)

read and modify the filter in c2g.py, then create any.gml
    
    $ python c2g.py

create html with inline svg

    $ python gml2svg.py any.gml > any.html

# note

* dont run ref.py, the code comes with all generated files
* c2g.py reads calccache and graphcache, so you dont have to calculate
  the graph weight again. Can take 10-15min if you remove the cache.
* change svg.tmpl to customize the output

# example filter for c2g.py

1. find all related embassies for the two embassies of intrest

    $ grep -E '(ALEXANDRIA|CAIRO)' edges.list | grep -Eo '[A-Z]+' | sort | uniq

2. remove useless values from the list and convert to a python dict

    e = ['ABUDHABI','ADDISABABA','ALEXANDRIA','ALGIERS',...]

3. create a sub-graph with the selection of vertices

    sg = g.subgraph(g.vs.select(_degree_gt=1, place_in=e))

4. find the clusters of the sub-graph. 

    for c in sg.clusters():

5. create another sub-graph for each cluster

    ssg = sg.subgraph(sg.vs.select(c))

6. save as .gml file

    ssg.write_gml('egypt-rel-%d.gml' % i)

7. find the clusters that include the initial embassies

    grep -lE '(ALEXANDRIA|CAIRO)' egypt-rel*gml

8. render the .gml with g2svg.py or gephi.org

for the full code check the "egypt" branch

# copyleft

GPLv3

# contact

need help? ask!

https://twitter.com/c2graph

