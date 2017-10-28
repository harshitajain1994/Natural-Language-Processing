#!/usr/bin/env python

import sys, fileinput
import tree

orig_stdout = sys.stdout
f = open('train.trees.pre', 'w')
sys.stdout = f

for line in fileinput.input("train.trees"):
    t = tree.Tree.from_str(line)

    # Binarize, inserting 'X*' nodes.
    t.binarize()

    # Remove unary nodes
    t.remove_unit()

    # The tree is now strictly binary branching, so that the CFG is in Chomsky normal form.

    # Make sure that all the roots still have the same label.
    assert t.root.label == 'TOP'

    print t
    
    
sys.stdout = orig_stdout
f.close()