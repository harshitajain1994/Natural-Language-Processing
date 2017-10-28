#!/usr/bin/env python

import sys, fileinput
from collections import defaultdict
from collections import OrderedDict
from operator import itemgetter
import tree
import operator

f = open('grammar', 'w')
dict = defaultdict(float)
dict_key_count = defaultdict(int)
# f = open('train.trees.pre.unk', 'w')
# sys.stdout = f
for line in fileinput.input("train.trees.pre.unk"):
	t = tree.Tree.from_str(line)
	# t.remove_unit()
	t.restore_unit()
	# t = tree.Tree.propogateParent(t)    
	dict = tree.Tree.get_dict(dict,t.root)
	# dict.update(d)
# for i in dict :
# 	print i,dict[i]

#getting the count for all the rules
for i in dict:
	word = i.split(" --> ")[0]
	dict_key_count[word] += dict[i]
	# dict[i] = dict[i]/dict_key_count[word]
	# print i, dict[i]

# calculating probabs
for i in dict : 
	word = i.split(" --> ")[0]
	dict[i] = dict[i]/dict_key_count[word]

#sorting the dictionary as per the probabilities
d = OrderedDict(sorted(dict.items(), key=itemgetter(1)))
for i in d :
	# print i,d[i]
	s = i + '#'+ str(d[i])
	f.write("{0}\n".format(s))
# sorted_x = sorted(dict.items(), key=operator.itemgetter(1))

# for i in sorted_x:
# 	f.write("{0}\n".format(i))
	# print i
f.close()





