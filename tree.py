import re

class Terminal(str):
    pass
    
class NT(str):
    def __repr__(self):
        return "NT("+str.__repr__(self)+")"
class Rule:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return "{} --> {}".format(self.lhs," ".join(self.rhs))
    def __repr__(self):
        return str(self)
    def __hash__(self):
        return hash(self.lhs) + hash(tuple(self.rhs))
    def __eq__(self,other):
        return self.lhs == other.lhs and len(self.rhs) == len(other.rhs) and all(s==o for s,o in zip(self.rhs,other.rhs))

class RHSWrapper:
    def __init__(self,rhs):
        self.rhs = rhs


class Tree:
    def __init__(self,node,children):
        self.node=node
        self.children = children
        self.parent = None
        for c in self.children:
            c.parent = self
    def __eq__(self,other):
        return self.node == other.node and len(self.children) == len(other.children) and all(selfc == otherc for selfc, otherc in zip(self.children,other.children))
    def to_str(self, d):
        if len(self.children)==0:
            return str(self.node)
        else:
            s = "("+self.node
            for child in self.children:
                s+="\n"+(d+1+len(self.node))*" "+child.to_str(d+4+len(self.node))
            return s+")"
    def __str__(self):
        return self.to_str(-len(self.node)+3)
    def copy(self):
        return Tree(self.node,[c.copy() for c in self.children])
        
    def rightmost_leave(self):
        if len(self.children) == 0:
            return self.node
        return self.children[-1].rightmost_leave()
    def leftmost_leave(self):
        if len(self.children) == 0:
            return self.node
        return self.children[0].leftmost_leave()
    def get_leaves(self):
        if len(self.children) == 0:
            return [self.node]
        l = []
        for c in self.children:
            l.extend(c.get_leaves())
        return l

    def dfs_addresses(self):
        yield []
        for i,c in enumerate(self.children):
            for addr in c.dfs_addresses():
                yield [i]+addr
                
                
    def get_subtree_by_address(self,address):
        tree = self
        try:
            for child_no in address:
                tree = tree.children[child_no]
        except IndexError:
            raise ValueError("There seems to be no addr "+str(address))
        return tree
        
    def substitute(self,address,new_subtree):
        if len(address)==0:
            self.node = new_subtree.node
            self.children = new_subtree.children
            return
        tree = self
        for child_no in address[:-1]:
            tree = tree.children[child_no]
        tree.children[address[-1]].node = new_subtree.node
        tree.children[address[-1]].children = new_subtree.children
    
    def leaves_left_of(self,addr):
        s = set()
        for subaddr in self.dfs_addresses(): #go through all addresses 
            if len(subaddr) <= len(addr) and addr[:len(subaddr)] != subaddr and all(ad>=subad for ad, subad in zip(addr,subaddr)):
                for leave in self.get_subtree_by_address(subaddr).get_leaves():
                    s.add(leave)
        return s
    def nonterminals_right_of(self,adresse):
        addr = list(adresse)
        while addr:
            pos = addr.pop()
            for i in range(pos+1,len(self.get_subtree_by_address(addr).children)):
                yield self.get_subtree_by_address(addr+[i]).node
        
    def extract_local_features(self,addr):
        features = dict()
        features["_DEPTH_"] = len(addr)
        if len(addr) == 0:
            return features
        for leave in self.leaves_left_of(addr):
            features["_LEFT_LEAVE_"+leave]=True
        for leave in self.nonterminals_right_of(addr):
            features["_RIGHT_NT_"+leave]=True
            
        if addr[-1]>0: #not the first child of the parent
            left_sister = self.get_subtree_by_address(addr[:-1] +  [addr[-1]-1])
            #features["RIGHTMOST_LEFT_SISTER"] = str(left_sister.rightmost_leave())
            #features["LEFTMOST_LEFT_SISTER"] = str(left_sister.leftmost_leave())
            features["_LEFT_SISTER_"] = str(left_sister.node)
        if len(self.get_subtree_by_address(addr[:-1]).children)-1> addr[-1]: #not the last child
            right_sister = self.get_subtree_by_address(addr[:-1] +  [addr[-1]+1])
            features["_RIGHT_SISTER_"] = str(right_sister.node)
            pass
            
        features["I'm_child_no"] = addr[-1]
        features["_PARENT_"] = str(self.get_subtree_by_address(addr[:-1]).node)
        
        if len(addr)>=2:
            features["_GRAND_PARENT_"] = str(self.get_subtree_by_address(addr[:-2]).node)
        #~ if len(addr)>=3:
            #~ for i in range(3,len(addr)-1):
                #~ features["_A_PARENT_"] = str(self.get_subtree_by_address(addr[:-i]).node)
            
        return features
            
    def extract_rules_with_features(self,addr=[]):
        features = self.extract_local_features(addr)
        curr_subtree = self.get_subtree_by_address(addr)
        non_terminals = [Terminal(c.node) if len(c.children)==0 else NT(c.node) for c in curr_subtree.children]
        rules = [(Rule(NT(curr_subtree.node),[Terminal(curr_subtree.node)]+non_terminals),features)]
        for i,c in enumerate(curr_subtree.children):
            if len(c.children)>0:
                rules.extend(self.extract_rules_with_features(addr+[i]) )
        return rules


def parse(expr):
    tokens = iter(tokenize(expr))
    try:
        t = tree(next(tokens), tokens)
    except ValueError:
        raise ValueError(expr)
    if len(list(tokens)) > 0: 
        raise ValueError(expr) #Liste an zu lesenden Tokens ist  n i c h t  leer
    return t

splt = re.compile("[\s,]|('|\()|(\))")

def tokenize(expr):
    l = list()
    in_anf = False
    letztes_war_anf = False
    sammel = []
    iterator = filter(lambda x: x != '' and not x is None,re.split(splt,expr.strip()))
    for w in iterator:
        if w=="'":
            if in_anf:
                letztes_war_anf = True
            in_anf = not(in_anf)
        if in_anf and w!="'":
            sammel.append(w)
        elif letztes_war_anf and len(sammel)>0:
            l.append("'"+" ".join(sammel)+"'")
            sammel = []
            letztes_war_anf = False
        elif w!="'":
            l.append(w)
            letztes_war_anf = False
    return l

def tree(token, rest):
    if token == ')':
        raise ValueError
    elif token == '(':
        label = next(rest)
        if label=='(':
            raise ValueError  # ( ist kein gutes Label
        children = trees(rest)
        return Tree(label,children)
    else:
        return Tree(token, [])

def trees(tokens):
    result = []
    for token in tokens:
        if token == ')':
            return result
        result.append(tree(token, tokens))
    raise ValueError #keine entsprechende schließende Klammer gefunden.
    
if __name__ == "__main__":
    t = parse("(query (area (keyval 'name','Paris'),(keyval 'is_in:country','France')),(nwr (keyval 'cuisine','japanese')),(qtype count))")
    print(t)
    print(t.extract_local_features([0]))
    
