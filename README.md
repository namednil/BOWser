# BOWser

BOWser is a very simple **B**ag **o**f **w**ords **s**emantic pars**er** that generates syntax trees of the target context free language conditioned on the words of the input string without considering the syntax of the natural language input. Everything is induced from the data, it just requires a parallel training file.

## Dependencies
only scikit-learn

## Input format
BOWser requires the training and test files to be in the following format:
\[natural language\] \[tab\] \[tree in lisp notation\]

## Test the parser
Go into the code of parse.py and set the path to the datasets you want to try, then simply run
python3 parse.py
