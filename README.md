# BOWser

BOWser is a very simple **B**ag **o**f **w**ords **s**emantic pars**er** that generates syntax trees of the target context free language conditioned on the words of the input string without considering the syntax of the natural language input. Everything is induced from the data, it just requires a parallel training file.

## Dependencies
only scikit-learn

## Input format
BOWser requires the training and test files to be in the following format:
\[natural language\] \[tab\] \[tree in lisp notation\]

## Test the parser
Go into the code of parse.py, set the path to the datasets and its start symbol you want to try, then simply run
python3 parse.py

##Performance
BOWser trains relatively fast (seconds to at most a few minutes) and gives surprisingly good results on some datasets that aren't too compositional.

| dataset                     | accuracy |
|-----------------------------|----------|
| Variable free geoquery-880  | 0.493    |
| nlmaps (English)            | 0.718    |
| nlmaps (German)             | 0.691    |
| Overnight: blocks           | 0.331    |
| Overnight: calendar         | 0.500    |
| Overnight: housing          | 0.455    |
| Overnight: recipes          | 0.704    |
| Overnight: recipes (German) | 0.479    |
Tried with varying activation functions (tanh or relu). With more feature engineering, slightly better results are to be expected.

It makes sense that BOWser performance not so well on geoquery because it tends to be more compositional. 
##Datasets and literature

- _Kwiatkowski et al. 10_: Inducing Probabilistic CCG Grammars from Logical Form with Higher-Order Unification
- variable free geoquery comes from [https://github.com/jimwhite/UBL] 
- _Wang et al. 15_: Building a Semantic Parser Overnight
- [Overnight datasets](https://worksheets.codalab.org/worksheets/0x269ef752f8c344a28383240f7bb2be9c/)
- [German Overnight recipes](https://github.com/polinastd/semparse)
- _Haas et al 16_: A Corpus and Semantic Parser for Multilingual Natural Language Querying of OpenStreetMap.
- [nlmaps corpus](http://www.cl.uni-heidelberg.de/statnlpgroup/nlmaps/)

