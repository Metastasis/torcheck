### relay search
https://metrics.torproject.org/rs.html


### DA's list
https://metrics.torproject.org/rs.html#search/flag\:authority


### General

Create installation instructions

##### main.py

Add closures in *_loop functions in order to save\pass global variables in initialization. 
Maybe create singleton for this purpose.

Encapsulate packet decisions logic in class.

##### blacklist.py

- add incremental\diff updates of blacklist
- write tests
