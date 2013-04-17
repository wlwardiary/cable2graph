# WikiLeaks Cablegate Reference Network Visualization

cable2graph is a collection of tools to create interactive 
HTML5/CSS3/SVG visualizations from graph data.

It is primarily written for the `cables.csv` file that contains 
the raw WikiLeaks cablegate data.

Three types of graphs are currently supported:

* undirected graph based on the manual references between cables
* weighted directed graph based on the sender and receiver of cables
* bipartite graph based on the TAGS value of each cable

## INSTALL

1. install [igraph 0.6](http://igraph.sourceforge.net/download.html) C library and Python extension module
2. install jinja2

    $ pip install jinja2

3. Download and unpack the zip archive of the github repository

https://github.com/wlwardiary/cable2graph/archive/master.zip

## USAGE

The typical workflow is divided in four steps:

1. extract features from the cables.csv (optional)
2. build the full graph
3. split the graph
4. create the visualization

### SHORT VERSION

    $ ./c2g full.graphml
    $ ./splitgraph --source full.graphml -d /tmp --multilevel --clusters
    $ ls /tmp/*graphml > /tmp/list-of-graphs
    $ ./g2svg -t graph-timeline.tmpl -i /tmp/list-of-graphs
    $ ./g2idx -i /tmp/list-of-graphs -d /tmp
    $ open /tmp/index.html

### EXTRACT

Extract features from the cables.csv into smaller plain text files stored in 
the data directory.

This step is optional. All files created by `extract` are included in the 
repository. A full run can take around 2-4 minutes.

    $ ./extract cables.csv

See below at the DATA section for more details.

### GRAPH

Create the large graph `full.graphml` with a file size of ~170MB.
    
    $ ./c2g full.graphml

The graph contains the following node and edge values:

* message reference number (MRN) as label
* the place part of the MRN
* missing with a value of 0 or 1 if the cable is referenced but 
  not included in the cables.csv
* unix timestamp for the time the cable was send
* the classification of the cable
* cable caption (currently only partial data)
* node degree
* pagerank
* authority
* constraint
* node [betweenness](https://en.wikipedia.org/wiki/Betweenness_centrality)

Node betweenness is based on the giant component of the full graph. 
Pre-calculated values are loaded from `data/betweenness`. Calculation of the 
Brandes betweenness takes around nine hours for the ~100,000 nodes and 
~143,000 edges of the giant component.

### SPLIT

Split the large graph into smaller clusters and communities.

    $ ./splitgraph --source full.graphml --multilevel --clusters

The `--cluster` option will export connected components but not the giant.

The giant component can be split using four different community detections.

* multilevel (Blondel, Guillaume, Lambiotte, Lefebvre, 2008)
* leading eigenvector (Newman)
* fastgreedy (Clauset, Newman, Moore, 2004)
* walktrap (Pons, Latapy)

Use the `--giant` option to save the giant component into a file.

The full graph or the giant component can be visualized with Gephi 
using the OpenOrd layout. The browser can display a SVG with around 800-1000 
nodes without performance issues.

### NEIGHBORHOOD

The `nbh` tool creates the neighborhood graph for a given node.
For multiple labels the directly related nodes are grouped together.

    $ echo "10EXAMPLE1" > list
    $ echo "09EXAMPLE2" >> list
    $ ./nbh full.graphml list

Not all cables have a neighborhood and `nbh` will never create the same 
graph twice.

### VISUALIZATION 

create HTML file with inline SVG from any .graphml:

    $ ./g2svg -g example.graphml

or use a list of graph files as source:

    $ ls cluster*graphml > list-of-clusters
    $ ./g2svg -i list-of-clusters

Two templates are currently included:

* svg.tmpl: graph with sidebar
* graph-timeline.tmpl: graph with timeline

    $ ./g2svg -t graph-timeline.tmpl -g example.graphml

The default layout algorithm is the force directed Kamada-Kawai (1989).
The `--layout` option can be used to specify any layout algorithm supported 
by igraph v0.6.

Useful are:

* `fruchterman_reingold` or `fr`
* `grid_fruchterman_reingold` or `gfr`
* `tree`
* `kamada_kawai` or `kk`

For a full list run:

    $ pydoc igraph.Graph.layout

### USAGE WITH GEPHI

For the integration with gephi existing layouts stored as x,y node attributes 
are supported by `g2svg`. Use the gephi `File -> Export` function.

Step by step how-to: https://github.com/wlwardiary/cable2graph/wiki/gephi

### GRAPH INDEX

The `g2idx` tool creates a index.html file for a list of given graphs
showing classification, TAGS and graph properties.

    $ ls *graphml > index-list
    $ ./g2idx -i index-list

## MAIN TOOLS

* `extract`: feature extraction from cables.csv
* `c2g`: create a graph from the reference data 
* `splitgraph`: split a graph into clusters and communities
* `nbh`: create a neighborhood graph for a list of MRN's
* `g2svg`: render graph layout and create svg

## MISC TOOLS

* `t2g`: create a graph from the TAGS data
* `r2g`: create a graph with the "from -> to" routing data
* `c2txt`: extract body and header from cables.csv
* `calcdates`: estimate date for missing MRN's
* `gen_colors`: create a random color for every place (see svg.css)

## DATA

* `data/wikileaks.org.map`: MRN to url mapping
* `data/all_ids.list`: all known MRN's
* `data/betweenness`: pre-calculated betweenness values form the giant
* `data/cable_ids.list`: all MRN's that exist in the cables.csv
* `data/captions.list`: cable captions mentioned in the REF: field
* `data/classifications.list`: MRN to classifications mapping
* `data/clique-big.list`: list of all clusters
* `data/clique.list`: list of all bigger cluster
* `data/dates.list`: all known dates for each MRN
* `data/dates_missing.list`: estimated dates for missing MRN's
* `data/diff_cnt.list`: how often is a missing MRN referenced
* `data/edges.list`: reference network
* `data/embassy.list`: embassy names from the MRN
* `data/from_to.list`: sender and receiver network
* `data/locations.list`: Locations name from the cvs header
* `data/missing_mrn.list`: referenced but missing MRN's
* `data/ref_ids.list`: referenced MRN's from cvs header
* `data/ref_regex_ids.list`: referenced MRN's from cable body
* `data/routing.codes`: telegram routing codes
* `data/subjects.list`: full extracted subject for each MRN
* `data/tags.program`: all program TAGS
* `data/tags.subject`: all subject TAGS
* `data/tags_edges.list`: TAGS network

## COPYLEFT

GPLv3

## CONTACT

https://twitter.com/datapornstar

