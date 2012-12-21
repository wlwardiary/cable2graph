# cables.csv to graph to svg

the short version

install igraph 0.6 with python bindings

install jinja2

    $ pip install jinja2

_[optional]_ extract features from the cables.csv into smaller plain text files

    $ ./extract cables.csv

create the large graph `full.graphml`
    
    $ ./c2g full.graphml

split the large graph into smaller clusters and communities

    $ ./splitgraph --source full.graphml --multilevel --clusters

create HTML file with inline SVG from any .graphml:

    $ ./g2svg -g any.graphml

or:

    $ ls cluster*graphml > list-of-clusters
    $ ./g2svg -i list-of-clusters

# note

* copy and customize the default svg.tmpl and run `g2svg` with `-t example.svg`.
* svg.tmpl referes to svg.js and svg.css
* use [ReVerb](http://reverb.cs.washington.edu/) to extract sentences from the cables and use `g2svg.py -r example.reverb`. To generate input files for ReVerb: `./c2txt cables.csv MRN1 MRN2 ...`.
* `./g2svg -h` for more options.
* you _don't_ need to run `extract`, the code comes with all generated data/ files.

# main tools

* `extract`: feature extraction from cables.csv
* `c2g`: create a graph from the reference data 
* `splitgraph`: split a graph into clusters and communities
* `nbh`: create a neighborhood graph for a list of MRN's
* `g2svg`: render graph layout and create svg

# misc tools

* `t2g`: create a graph from the TAGS data
* `r2g`: create a graph with the "from -> to" routing data
* `c2txt`: extract body and header from cables.csv
* `calcdates`: estimate date for missing MRNs
* `gen_colors`: create a random color for every place (see svg.css)

# copyleft

GPLv3

# contact

https://twitter.com/c2graph

