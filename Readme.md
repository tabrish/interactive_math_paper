Welcome! We are building a python script to convert latex files to html, with the goal of adding features to make math papers easier and more fun to read. The main features we have at the moment are:
 - proofs are collapsible/click-to-expand
 - if a word is defined, hovering over that word anywhere in the paper displays the definition
 - if a theorem/lemma/etc is referenced later in a paper, hovering over “Theorem X” displays the statement of Theorem X

Check out our examples of converted papers in the Documentation!

## Installation

Clone the repository and then install the python module using
```bash
    pip install -e .
```

you can then run the script using the following command
``` bash
    convert-paper [input_file] [output_file]
```
