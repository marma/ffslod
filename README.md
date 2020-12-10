# FFSLOD
A dockerized tool to force Linked data and SPARQL support out of an obstructing site through a combination of RDFa, URL and content negotiation, or as a last attempt: a separate site for identifiers and parsing HTML with regexp.

### Background
There are many sites that hold structured or semi-structured data yet fail to provide this in a machine readable form, i.e through robust identifiers, content negotiation, RDFa, XSLT, embedded JSON-LD or other ways to convey semantics. This can be because of not being aware that providing information this way would be valuable, but is often a consequence of having little or no control over the proided service. This, in turn, is often the result of having bought a web platform with no support for embedded machine readable data.

Since organisations have different varying level of control over their sites FFSLOD aims to provide a simple way to at least provide some semantics, and SPARQL support, using a number of modes of operation. It can be used to simply redirect more persistant URIs to "ugly" ones, or to set up a completely separate "id-domain" that will extract data from the offending site.

![alt text](https://raw.githubusercontent.com/marma/ffslod/main/etc/FFSLOD.png "Modes of operation")

## Installation

## Configuration
