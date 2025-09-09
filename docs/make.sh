#!/bin/bash
pdoc interactive_math_paper -o ./docs/html -t ./docs/templates
convert-paper ./texfiles/tree_decompositions_and_many-sided_separations.tex ./docs/html/example_papers/tree_decompositions_and_many-sided_separations.html
