#!/usr/bin/env python

import sys, fileinput
import tree

orig_stdout = sys.stdout
f = open('dev.parses.post', 'w')
sys.stdout = f
for line in fileinput.input('dev.parses'):
    t = tree.Tree.from_str(line)
    if t.root is None:
        print
        continue
    t.restore_unit()
    t.unbinarize()

    print t
    
sys.stdout = orig_stdout
f.close()    
    
