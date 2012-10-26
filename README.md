# cables.csv to graph to svg

the short version

_[optional]_ create list of IDs and edges as plain text files:

    $ python extract.py cables.csv

Edit and modify the filter in `c2g.py` (see example below), and run it to create [say] `any.gml`:
    
    $ python c2g.py

create html with inline svg:

    $ pthon g2svg.py -g any.gml

# note

* You _don't_ need to run `extract.py`, the code comes with all generated files.
* c2g.py reads calccache and graphcache, so you dont have to calculate
  the graph weight again. Can take 10-15min if you remove the cache.
* You can customize svg.tmpl (example: `svg-jquery-tooltip.tmpl`), and run `g2svg.py` with `-t yourtemplate.svg`.
* You can use [ReVerb](http://reverb.cs.washington.edu/) to extract sentences from the relevant cables (example: `il-relative.reverb`) and use `-r yourstuff.reverb`. To generate input files for ReVerb: `python c2txt.py cables.csv ID1 ID2 ...`.
* `python g2svg.py -h` for more options.

# example filter for c2g.py

find all related embassies for the two embassies of intrest

    $ grep -E '(ALEXANDRIA|CAIRO)' edges.list | grep -Eo '[A-Z]+' | sort | uniq

remove useless values from the list and convert to a python dict

    e = ['ABUDHABI','ADDISABABA','ALEXANDRIA','ALGIERS',...]

create a sub-graph with the selection of vertices

    sg = g.subgraph(g.vs.select(_degree_gt=1, place_in=e))

find the clusters of the sub-graph. 

    for c in sg.clusters():

create another sub-graph for each cluster

    ssg = sg.subgraph(sg.vs.select(c))

save as .gml file

    ssg.write_gml('egypt-rel-%d.gml' % i)

find the clusters that include the initial embassies

    grep -lE '(ALEXANDRIA|CAIRO)' egypt-rel*gml

render the .gml with g2svg.py or gephi.org

for the full code check the "egypt" branch

# copyleft

GPLv3

# contact

need help? ask!

https://twitter.com/c2graph

