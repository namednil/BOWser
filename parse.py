import re
from generator import SemanticGenerator
from tree import Tree, parse,NT

from time import time


def word_tokenize(sent):
    return list(filter(lambda s: isinstance(s,str) and len(s)>0,re.split('\s|([.,;?!])',sent)))


def nl_features(sent,dictionary):
    tokens = word_tokenize(sent)
    l = len(tokens)
    for w in tokens:
        dictionary[w.lower()] = True
    #dictionary["COUNT_CAPS"] = sum(w[0].upper() == w[0] for w in tokens)

generator = SemanticGenerator(NT("answer")) #set the starting Nonterminal, for geoquery: answer, for nlmaps: query, for overnight datasets: listValue

def semparse(sent):
    d = dict()
    nl_features(sent,d)
    print(generator.greedy_generate(d))
    
t1 = time()
print("Reading corpus...")
with open("datasets/geo/train.txt") as f: #nlmaps.train.enlisp
    for line in f:
        nl, mrl = line.split("\t")
        try:
            t = parse(mrl)
        except ValueError:
            print("PARSE-ERROR:",line)
            continue
        #print(t)
        rules_and_features = t.extract_rules_with_features()
        for rule, instanceDict in rules_and_features:
            nl_features(nl,instanceDict)
            #print(rule,instanceDict)
            generator.addInstance(rule, instanceDict)
        #input()
t2 = time()
print("done...took {}s".format(round(t2-t1,4)))
print("Training...")
generator.train()
t3 = time()
print("done...took {}s".format(round(t3-t2,4)))

with open("datasets/geo/test.txt") as f: #nlmaps.test.enlisp
    korrekt = 0
    total = 0
    for i,line in enumerate(f):
        nl, mrl = line.split("\t")
        try:
            t = parse(mrl)
        except ValueError:
            print("PARSE-ERROR:",line)
        d = dict()
        nl_features(nl,d)
        if generator.compare(nl,d,t,verbose=False):
            korrekt +=1
        total +=1
        #~ if i%100 == 0:
            #~ print(i)
        
    print("Accuracy:",korrekt,korrekt/total,total)

