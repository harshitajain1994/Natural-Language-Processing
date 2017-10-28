Built a simple constituency parser trained from the ATIS portion of the Penn Treebank. 

The file train.trees contains a sequence of trees, one per line, each in the following format: (TOP (S (VP (VB Book) (NP (DT that) (NN flight)))) (PUNC .)) 

Run train.trees through preprocess.py and save the output to train.trees.pre. This script makes the trees strictly binary branching. When it binarizes, it inserts nodes with labels of the form X*, and when it removes unary nodes, it fuses labels so they look like X_Y . 
Run train.post through postprocess.py and verify that the output is identical to the original train.trees. This script reverses all the modifications made by preprocess.py. 
Run train.trees.pre through unknown.py and save the output to train.trees.pre.unk. This script replaces all words that occurred only once with the special symbol <unk>. 

To evaluate the parser output against the correct trees in dev.trees use the command: 

python evalb.py dev.parses.post dev.trees
