# tree.py
# David Chiang <chiang@isi.edu>

import re
from collections import defaultdict

class RootDeletedException(Exception):
    pass

class Node(object):
    def __init__(self, label, children):
        self.label = label
        self.children = children
        for (i,child) in enumerate(self.children):
            if child.parent is not None:
                child.detach()
            child.parent = self
            child.order = i
        self.parent = None
        self.order = 0

    def __str__(self):
        return self.label

    def _subtree_str(self):
        if len(self.children) != 0:
            return "(%s %s)" % (self.label, " ".join(child._subtree_str() for child in self.children))
        else:
            s = '%s' % self.label
            #s = s.replace("(", "-LRB-")
            #s = s.replace(")", "-RRB-")
            return s

    def insert_child(self, i, child):
        if child.parent is not None:
            child.detach()
        child.parent = self
        self.children[i:i] = [child]
        for j in range(i,len(self.children)):
            self.children[j].order = j

    def append_child(self, child):
        if child.parent is not None:
            child.detach()
        child.parent = self
        self.children.append(child)
        child.order = len(self.children)-1

    def delete_child(self, i):
        self.children[i].parent = None
        self.children[i].order = 0
        self.children[i:i+1] = []
        for j in range(i,len(self.children)):
            self.children[j].order = j

    def detach(self):
        if self.parent is None:
            raise RootDeleteException
        self.parent.delete_child(self.order)

    def delete_clean(self):
        "Cleans up childless ancestors"
        parent = self.parent
        self.detach()
        if len(parent.children) == 0:
            parent.delete_clean()

    def bottomup(self):
        for child in self.children:
            for node in child.bottomup():
                yield node
        yield self

    def leaves(self):
        if len(self.children) == 0:
            yield self
        else:
            for child in self.children:
                for leaf in child.leaves():
                    yield leaf

class Tree(object):
    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root._subtree_str()

    interior_node = re.compile(r"\s*\(([^\s)]*)")
    close_brace = re.compile(r"\s*\)")
    leaf_node = re.compile(r'\s*([^\s)]+)')

    @staticmethod
    def _scan_tree(s):
        result = Tree.interior_node.match(s)
        if result != None:
            label = result.group(1)
            pos = result.end()
            children = []
            (child, length) = Tree._scan_tree(s[pos:])
            while child != None:
                children.append(child)
                pos += length
                (child, length) = Tree._scan_tree(s[pos:])
            result = Tree.close_brace.match(s[pos:])
            if result != None:
                pos += result.end()
                return Node(label, children), pos
            else:
                return (None, 0)
        else:
            result = Tree.leaf_node.match(s)
            if result != None:
                pos = result.end()
                label = result.group(1)
                #label = label.replace("-LRB-", "(")
                #label = label.replace("-RRB-", ")")
                return (Node(label,[]), pos)
            else:
                return (None, 0)

    @staticmethod
    def from_str(s):
        s = s.strip()
        (tree, n) = Tree._scan_tree(s)
        return Tree(tree)

    #added methods here
    @staticmethod
    def get_dict(d,root):
        d = Tree.print_dict(d,root)
        return d

    @staticmethod
    def propogateParent(tree):
        tree.root = Tree.propogateParentRoot(tree.root)
        return tree

    @staticmethod
    def propogateParentRoot(root):
        if root is None :
            return root

        if len(root.children) == 2:
            for i in range(len(root.children)) :
                root.children[i] = Tree.propogateParentRoot(root.children[i])
                root.children[i].label = root.children[i].label +"^" +root.label
                

        return root


    # @staticmethod
    # def print_dict(d,root):
    #     if root is None:
    #         return d

    #     children = root.children

    #     if len(children) is 0:
    #         return d

    #     s = root.label + " --> " 
    #     for child in children :
    #         s += child.label 
    #         s += " "
    #         d = Tree.print_dict(d,child)

    #     # print s
    #     d[s] += 1
    #     return d


    @staticmethod
    def print_dict(d,root):
        if root is None:
            return d

        children = root.children

        if len(children) is 0:
            return d

        s = root.label + " --> " 
        for child in children :
            s += child.label 
            s += " "
            d = Tree.print_dict(d,child)

        # print s
        d[s] += 1
        return d

    def bottomup(self):
        """ Traverse the nodes of the tree bottom-up. """
        return self.root.bottomup()

    def leaves(self):
        """ Traverse the leaf nodes of the tree. """
        return self.root.leaves()

    def remove_empty(self):
        """ Remove empty nodes. """
        nodes = list(self.bottomup())
        for node in nodes:
            if node.label == '-NONE-':
                try:
                    node.delete_clean()
                except RootDeletedException:
                    self.root = None

    def remove_unit(self):
        """ Remove unary nodes by fusing them with their parents. """
        nodes = list(self.bottomup())
        for node in nodes:
            if len(node.children) == 1:
                child = node.children[0]
                if len(child.children) > 0:
                    node.label = "%s_%s" % (node.label, child.label)
                    child.detach()
                    for grandchild in list(child.children):
                        node.append_child(grandchild)

    def restore_unit(self):
        """ Restore the unary nodes that were removed by remove_unit(). """
        def visit(node):
            children = [visit(child) for child in node.children]
            labels = node.label.split('_')
            node = Node(labels[-1], children)
            for label in reversed(labels[:-1]):
                node = Node(label, [node])
            return node
        self.root = visit(self.root)

    def binarize_right(self):
        """ Binarize into a right-branching structure. """
        nodes = list(self.bottomup())
        for node in nodes:
            if len(node.children) > 2:
                # create a right-branching structure
                children = list(node.children)
                children.reverse()
                vlabel = node.label+"*"
                prev = children[0]
                for child in children[1:-1]:
                    prev = Node(vlabel, [child, prev])
                node.append_child(prev)

    def binarize_left(self):
        """ Binarize into a left-branching structure. """
        nodes = list(self.bottomup())
        for node in nodes:
            if len(node.children) > 2:
                vlabel = node.label+"*"
                children = list(node.children)
                prev = children[0]
                for child in children[1:-1]:
                    prev = Node(vlabel, [prev, child])
                node.insert_child(0, prev)

    def binarize(self):
        """ Binarize into a left-branching or right-branching structure
        using linguistically motivated heuristics. Currently, the heuristic
        is extremely simple: SQ is right-branching, everything else is left-branching. """
        nodes = list(self.bottomup())
        for node in nodes:
            if len(node.children) > 2:
                if node.label in ['SQ']:
                    # create a right-branching structure
                    children = list(node.children)
                    children.reverse()
                    vlabel = node.label+"*"
                    prev = children[0]
                    for child in children[1:-1]:
                        prev = Node(vlabel, [child, prev])
                    node.append_child(prev)
                else:
                    # create a left-branching structure
                    vlabel = node.label+"*"
                    children = list(node.children)
                    prev = children[0]
                    for child in children[1:-1]:
                        prev = Node(vlabel, [prev, child])
                    node.insert_child(0, prev)

    def unbinarize(self):
        """ Undo binarization by removing any nodes ending with *. """
        def visit(node):
            children = sum([visit(child) for child in node.children], [])
            if node.label.endswith('*'):
                return children
            else:
                return [Node(node.label, children)]
        roots = visit(self.root)
        assert len(roots) == 1
        self.root = roots[0]

if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        t = Tree.from_str(line)
        print t
        
