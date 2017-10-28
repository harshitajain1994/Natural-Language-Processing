#!/usr/bin/env python

import sys, fileinput
from collections import defaultdict
# import tree
import operator
from numpy import *
from nltk import word_tokenize
from sets import Set
import time
from math import log10
import matplotlib.pyplot as plt

# class code here
# class MyNode(object):
# 	def __init__(self, label):
# 		self.val = label
# 		self.left = None
# 		self.right = None
		 

# class MyTree(object):
# 	def __init__(self, root):
# 		self.root = root

f = open('dev.parses', 'w')
prob_dict = defaultdict(double)
rule_dict = defaultdict(set)

#storing the grammar rules as probs, and Y Z -> X (for rule X -> Y Z)
for line in fileinput.input("grammar"):
	words = line.split('#')
	rule_parts = words[0].strip().split(" --> ")
	prob_dict[words[0].strip()] = log10(double(words[1]))
	rule_dict[rule_parts[1]].add(rule_parts[0])

# def preorder(s,root) :
# 	if root is None :
# 		return s
# 	s += ' '
# 	s += root.val
# 	s = preorder(s,root.left)
# 	s = preorder(s,root.right)
# 	return s

def getTree(s,rootValList, i, j,label) :
	s = s + '(' + label + ' '	
	flag_terminal = True
	
	# node = MyNode(label)
	k = rootValList[1]
	if type(k) is int :
		flag_terminal = False



	# t = MyTree(node)
	if flag_terminal :
		if k == '<unk>' :
			k = rootValList[2]
		s = s + k + ')'
		# t.root.left = MyNode(k)
		# t.root.right = None
	else:
		left = rootValList[2]
		right = rootValList[3]
		s = getTree(s,Matrix[i][k][left],i,k,left)
		s = getTree(s,Matrix[k][j][right],k,j,right)
		s = s+')'
	
	return s



# print prob_dict
# count = 0
# for i in rule_dict :
# 	count += 1

# print "count",count
# print rule_dict['<unk>']

 # reading input
# line = 'Show me the fare .'

# plt.yscale('log')
# plt.xscale('log')
# plt.subplot(222)
for line in fileinput.input('dev.strings') :
	start_time = time.clock()
	# print line

	
	words = word_tokenize(line)
	n = len(words) 

	Matrix = [[0 for x in range(n+1)] for y in range(n+1)] 
	for i in range(n) :
		#adding the terminal values
		Matrix[i][i+1] = {}
		if words[i] in rule_dict :
			for x in rule_dict[words[i]] :
				s = x + ' --> ' + words[i]
				Matrix[i][i+1][x] = [prob_dict[s],words[i]] # a list 
				# Matrix[i][i+1]['backpointer'] = words[i]
		else :
			for x in rule_dict['<unk>'] :
				s = x + " --> <unk>" 
				Matrix[i][i+1][x] = [prob_dict[s],'<unk>',words[i]] # replacing the unkown words with <unk>
				# Matrix[i][i+1]['backpointer'] = '<unk>'
		# print Matrix[i][i+1],i



	for j in range(2,n+1) :
		# print j
		for i in range(n+1-j) :
			# print i,j+i
			Matrix[i][i+j] = {} # dictionary for every cell
			for k in range(i+1,j+i) :
				d1 = Matrix[i][k] # sets of possible
				d2 = Matrix[k][j+i]
				# print i,k,j+i
				if len(d1) != 0 and len(d2) != 0:
					for a in d1 :
						for b in d2:
							# print a,b
							s = a+ " "+b
							if s in rule_dict:
								for x in rule_dict[s] :
									rule = x+ ' --> ' +s
									probab = double(d1[a][0]) + double(d2[b][0]) + double(prob_dict[rule])
									# probab = log10(double(d1[a][0])) + log10(double(d2[b][0])) + log10(double(prob_dict[rule]))
									if x in Matrix[i][i+j] :
										Matrix[i][i+j][x][0] = max(probab,Matrix[i][i+j][x][0])# max of temp and this
										if Matrix[i][i+j][x][0] == probab :
											# Matrix[i][i+j]['backpointer'] = k
											Matrix[i][i+j][x] = [probab,k,a,b]
									else :
										Matrix[i][i+j][x] = [probab,k,a,b]
										# Matrix[i][i+j]['backpointer'] = k
										# Matrix[i][i+j][x][1] = k
									# print rule_dict[s],s
			# print len(Matrix[i][j+i])
			# myList = Set([])
			# for key in Matrix[i][j+i]:
			# 	if len(rule_dict[key]) > 0 :
			# 		for val in rule_dict[key] :
			# 			myList.add(val)

			# # print myList
			
			# for val in myList :
			# 	Matrix[i][i+j][val] =Matrix[i][i+j][x]
				# print len(myList),key
			# for val in myList :
			# 	print val
			# 	Matrix[i][j+i][val] = [0,0,val,0]



	if len(Matrix[0][n]) == 1 :
		start_time = time.clock() - start_time
		# print Matrix[0][n]['TOP'][0]
		# print '(TOP '
		f.write("{0}\n".format(getTree('',Matrix[0][n]['TOP'],0,n,'TOP')))
		# print 
		
		sen_len = len(words)
		# plt.plot(sen_len, start_time)
		# plt.loglog(x, y, basex=10, basey=10, linestyle='None', marker='x', markeredgecolor='red')
		# plt.show()
		# print start_time,"time" 
	else :
		# s = 'dfsNULL'
		f.write("{0}\n".format(''))
		print "no"

plt.show()
f.close()

# for i in sorted_x:
# 	f.write("{0}\n".format(i))
# 	# print i


