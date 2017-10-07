#from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from sklearn.feature_extraction import DictVectorizer
from heapq import heappush, heappop,heapify, merge
from math import log
from tree import Tree,NT,Terminal,Rule

import multiprocessing as mp
from os import sched_getaffinity #how many cpus are available?

def train_a_classifier(classifierType,lhs,relevant_data, labels):
    #print("Training "+lhs)
    clf = classifierType()
    clf.fit(relevant_data,labels)
    return (lhs,clf)

def getClassifier():
    return MLPClassifier(hidden_layer_sizes=(150,),random_state=7,activation='tanh',early_stopping=False,validation_fraction=0.1,tol=0.00001, verbose=False, max_iter=240)

class SemanticGenerator:
    def __init__(self,startsymbol):
        assert(isinstance(startsymbol, NT))
        self.start = startsymbol
        self.classifierType =  getClassifier
        self.classifiers = dict()
        self.vectorizers = dict() 
        self.instances=[]
        self.rules_used = []
        self.rules = dict()
        
    def addInstance(self,rule,instanceDict):
        if rule.lhs not in self.rules:
            self.rules[rule.lhs] = {rule}
        else:
            self.rules[rule.lhs].add(rule)
        self.instances.append(instanceDict)
        self.rules_used.append(rule)
        
    def train(self):
        val_scores = []
        classifiers_trained = []
        todo_list = []
        for lhs,rules in self.rules.items():
            if len(rules)>1:
                relevant_data = []
                labels = []
                for dictinstance, rule in zip(self.instances, self.rules_used):
                    if rule.lhs == lhs:
                        relevant_data.append(dictinstance)
                        labels.append(rule.rhs.__repr__()) #the classfication requires classes of type string
                clf = self.classifierType()
                self.vectorizers[lhs] = DictVectorizer(sparse=True)
                data = self.vectorizers[lhs].fit_transform(relevant_data)
                todo_list.append((self.classifierType,lhs,data,labels))
                #clf.fit(data,labels)
                #~ try:
                    #~ val_scores.append(clf.validation_scores_[-1])
                    #~ classifiers_trained.append(lhs)
                #~ except AttributeError:
                    #~ pass
                #self.classifiers[lhs] =  clf
        cpu_count = len(sched_getaffinity(0))
        with mp.Pool(cpu_count) as p:
            self.classifiers = dict(p.starmap(train_a_classifier,todo_list))
        
    def greedy_generate(self, instanceDict,tree=None,d=0):
        if tree is None:
            tree = Tree(NT(self.start),[])
        if d>50:
            return None
        chosen_rhs = None
        for addr in tree.dfs_addresses():
            subtree = tree.get_subtree_by_address(addr)
            if isinstance(subtree.node, NT):
                features = tree.extract_local_features(addr)
                for (key,val) in instanceDict.items(): #add local tree features
                    features[key] = val
                if str(subtree.node) in self.classifiers:
                    instance = self.vectorizers[str(subtree.node)].transform(features)
                    chosen_rhs = self.classifiers[str(subtree.node)].predict(instance)[0]
                    chosen_rhs = eval(chosen_rhs) #restore actual rhs from string
                else: #if there's no such classifier, then there as to be exactly one rule!
                    assert(len(self.rules[str(subtree.node)])==1)
                    chosen_rhs = list(self.rules[str(subtree.node)])[0].rhs
                break
        if chosen_rhs is None:
            return tree
        #print(chosen_rhs)
        new_subtree = Tree(Terminal(tree.get_subtree_by_address(addr)),[Tree(symbol,[]) for symbol in chosen_rhs[1:]]) #don't include query, area, keyval as terminal symbols again (twice)
        tree.substitute(addr,new_subtree)
        return self.greedy_generate(instanceDict,tree,d+1)        
        
    def compare(self, nl,instanceDict,goldTree,verbose=False):
        generated_tree = self.greedy_generate(instanceDict)
        r = generated_tree == goldTree
        if verbose and not r:
            print(nl)
            print("gold",goldTree)
            print(generated_tree)
        return r
