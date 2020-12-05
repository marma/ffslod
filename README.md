# FFSLOD
A dockerized tool to force Linked data and SPARQL support out of an obstructing site through a combination of RDFa, URL and content negotiation, or as a last attempt: a separate site for identifiers and parsing HTML with regexp.

There are many sites that hold structured or semi-structured data yet fail to provide this in a machine readable form, i.e through robust identifiers, content negotiation, RDFa, embedded JSON-LD or other ways to convey semantics. This can be because of of being aware that providing information this way is valuable, but is often a consequence of having little or no control over the proided service. This, in turn, is often the result of having bought a web platform with no support for microdata, Linked data, etc.

![alt text](https://raw.githubusercontent.com/marma/ffslod/main/etc/FSSLOD.png "Modes of operation")
