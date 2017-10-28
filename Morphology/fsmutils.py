import os, sys, re, random, tempfile

"""
Finite state transducers.

A finite state trasducer, or FST, is a directed graph that is used to
encode a mapping from a set of I{input strings} to a set of I{output
strings}.  An X{input string} is a sequence of immutable values (such
as integers, characters, or strings) called X{input symbols}.
Similarly, an C{output string} is a sequence of immutable values
called X{output symbols}.  Collectively, input strings and output
strings are called X{symbol strings}, or simply X{strings} for short.
Note that this notion of I{string} is different from the python string
type -- symbol strings are always encoded as tuples of input or output
symbols, even if those symbols are characters.  Also, note that empty
sequences are valid symbol strings.

The nodes of an FST are called X{states}, and the edges are called
X{transition arcs} or simply X{arcs}.  States may be marked as
X{final}, and each final state is annotated with an output string,
called the X{finalizing string}.  Each arc is annotated with an input
string and an output string.  An arc with an empty input string is
called an I{epsilon-input arc}; and an arc with an empty output
string is called an I{epsilon-output arc}.

The set of mappings encoded by the FST are defined by the set of paths
through the graph, starting at a special state known as the X{initial
state}, and ending at a final state.  In particular, the FST maps an
input string X to an output string Y iff there exists a path from the
initial state to a final state such that:

  - The input string X is formed by concatenating the input strings
    of the arcs along the path (in order).
  - The output string Y is formed by concatenating the output strings
    of the arcs along the path (in order), plus the final state's
    output string.

The following list defines some terms that apply to finite state
transducers.

  - The X{transduction} defined by a FST is the mapping from input
    strings to output strings.

  - An FST X{encodes a deterministic transduction} if each input
    string maps to at most one output string.  An FST X{encodes a
    nondeterministic transduction} if any input string maps to more
    than one output string.

  - An FST is X{deterministic} if it every state contains at most one
    outgoing arc that is consistent with any input string; otherwise,
    the FST is X{nondeterministic}.  If an FST is deterministic, then
    it necessarily encodes a deterministic transduction; however, it
    is possible to define an FST that is nondeterministic but that
    encodes a deterministic transduction.

  - An FST is X{sequential} if each arc is labeled with exactly one
    input symbol, no two outgoing arcs from any state have the same
    input symbol, and all finalizing strings are empty.  (Sequential
    implies deterministic).

  - An FST is I{subsequential} if each arc is labeled with exactly
    one input symbol, and no two outgoing arcs from any state have
    the same input symbol.  (Finalizing strings may be non-empty.)

An FSA can be represented as an FST that generates no output symbols.

The current FST class does not provide support for:

  - Weighted arcs.  (However, weights can be used as, or included
    in, the output symbols.  The total weight of a path can then
    be found after transduction by combining the weights.  But
    there's no support for e.g., finding the path with the minimum
    weight.

  - Multiple initial states.

  - Initializing strings (an output string associated with the initial
    state, which is always generated when the FST begins).

Possible future changes:

  - Define several classes, in a class hierarchy?  E.g., FSA is a base
    class, FST inherits from it.  And maybe a further subclass to add
    finalizing sequences.  I would need to be more careful to only
    access the private variables when necessary, and to usually go
    through the accessor functions.
"""


######################################################################
#{ Finite State Transducer
######################################################################

class FST(object):
    """
    A finite state transducer.  Each state is uniquely identified by a
    label, which is typically a string name or an integer id.  A
    state's label is used to access and modify the state.  Similarly,
    each arc is uniquely identified by a label, which is used to
    access and modify the arc.

    The set of arcs pointing away from a state are that state's
    I{outgoing} arcs.  The set of arcs pointing to a state are that
    state's I{incoming} arcs.  The state at which an arc originates is
    that arc's I{source} state (or C{src}), and the state at which it
    terminates is its I{destination} state (or C{dst}).

    It is possible to define an C{FST} object with no initial state.
    This is represented by assigning a value of C{None} to the
    C{initial_state} variable.  C{FST}s with no initial state are
    considered to encode an empty mapping.  I.e., transducing any
    string with such an C{FST} will result in failure.
    """
    def __init__(self, label):
        """
        Create a new finite state transducer, containing no states.
        """
        self.label = label
        """A label identifying this FST.  This is used for display &
        debugging purposes only."""

        #{ State Information
        self._initial_state = None
        """The label of the initial state, or C{None} if this FST
        does not have an initial state."""

        self._incoming = {}
        """A dictionary mapping state labels to lists of incoming
        transition arc labels."""

        self._outgoing = {}
        """A dictionary mapping state labels to lists of outgoing
        transition arc labels."""

        self._is_final = {}
        """A dictionary mapping state labels to boolean values,
        indicating whether the state is final."""

        self._finalizing_string = {}
        """A dictionary mapping state labels of final states to output
        strings.  This string should be added to the output
        if the FST terminates at this state."""

        self._state_descr = {}
        """A dictionary mapping state labels to (optional) state
        descriptions."""
        #}

        #{ Transition Arc Information
        self._src = {}
        """A dictionary mapping each transition arc label to the label of
        its source state."""

        self._dst = {}
        """A dictionary mapping each transition arc label to the label of
        its destination state."""

        self._in_string = {}
        """A dictionary mapping each transition arc label to its input
        string, a (possibly empty) tuple of input symbols."""

        self._out_string = {}
        """A dictionary mapping each transition arc label to its output
        string, a (possibly empty) tuple of input symbols."""

        self._arc_descr = {}
        """A dictionary mapping transition arc labels to (optional)
        arc descriptions."""
        #}

    #////////////////////////////////////////////////////////////
    #{ State Information
    #////////////////////////////////////////////////////////////

    def states(self):
        """Return an iterator that will generate the state label of
        each state in this FST."""
        return iter(self._incoming)

    def has_state(self, label):
        """Return true if this FST contains a state with the given
        label."""
        return label in self._incoming

    def _get_initial_state(self):
        return self._initial_state
    def _set_initial_state(self, label):
        if label is not None and label not in self._incoming:
            raise ValueError('Unknown state label %r' % label)
        self._initial_state = label
    initial_state = property(_get_initial_state, _set_initial_state,
                             doc="The label of the initial state (R/W).")

    def incoming(self, state):
        """Return an iterator that will generate the incoming
        transition arcs for the given state.  The effects of modifying
        the FST's state while iterating are undefined, so if you plan
        to modify the state, you should copy the incoming transition
        arcs into a list first."""
        return iter(self._incoming[state])

    def outgoing(self, state):
        """Return an iterator that will generate the outgoing
        transition arcs for the given state.  The effects of modifying
        the FST's state while iterating are undefined, so if you plan
        to modify the state, you should copy the outgoing transition
        arcs into a list first."""
        return iter(self._outgoing[state])

    def is_final(self, state):
        """Return true if the state with the given state label is
        final."""
        return self._is_final[state]

    def finalizing_string(self, state):
        """Return the output string associated with the given final
        state.  If the FST terminates at this state, then this string
        will be emitted."""
        #if not self._is_final[state]:
        #    raise ValueError('%s is not a final state' % state)
        return self._finalizing_string.get(state, ())

    def state_descr(self, state):
        """Return the description for the given state, if it has one;
        or None, otherwise."""
        return self._state_descr.get(state)

    #////////////////////////////////////////////////////////////
    #{ Transition Arc Information
    #////////////////////////////////////////////////////////////

    def arcs(self):
        """Return an iterator that will generate the arc label of
        each transition arc in this FST."""
        return iter(self._src)

    def src(self, arc):
        """Return the state label of this transition arc's source
        state."""
        return self._src[arc]

    def dst(self, arc):
        """Return the state label of this transition arc's destination
        state."""
        return self._dst[arc]

    def in_string(self, arc):
        """Return the given transition arc's input string, a (possibly
        empty) tuple of input symbols."""
        return self._in_string[arc]

    def out_string(self, arc):
        """Return the given transition arc's output string, a
        (possibly empty) tuple of output symbols."""
        return self._out_string[arc]

    def arc_descr(self, arc):
        """Return the description for the given transition arc, if it
        has one; or None, otherwise."""
        return self._arc_descr.get(arc)

    def arc_info(self, arc):
        """Return a tuple (src, dst, in_string, out_string) for the
        given arc, where:
          - C{src} is the label of the arc's source state.
          - C{dst} is the label of the arc's destination state.
          - C{in_string} is the arc's input string.
          - C{out_string} is the arc's output string.
        """
        return (self._src[arc], self._dst[arc],
                self._in_string[arc], self._out_string[arc])

    #////////////////////////////////////////////////////////////
    #{ FST Information
    #////////////////////////////////////////////////////////////

    def is_sequential(self):
        """
        Return true if this FST is sequential.
        """
        for state in self.states():
            if self.finalizing_string(state): return False
        return self.is_subsequential()

    def is_subsequential(self):
        """
        Return true if this FST is subsequential.
        """
        for state in self.states():
            out_syms = set()
            for arc in self.outgoing(state):
                out_string = self.out_string(arc)
                if len(out_string) != 1: return False
                if out_string[0] in out_syms: return False
                out_syms.add(out_string)
        return True

    #////////////////////////////////////////////////////////////
    #{ State Modification
    #////////////////////////////////////////////////////////////

    def add_state(self, label=None, is_final=False,
                  finalizing_string=(), descr=None):
        """
        Create a new state, and return its label.  The new state will
        have no incoming or outgoing arcs.  If C{label} is specified,
        then it will be used as the state's label; otherwise, a new
        unique label value will be chosen.  The new state will be
        final iff C{is_final} is true.  C{descr} is an optional
        description string for the new state.

        Arguments should be specified using keywords!
        """
        label = self._pick_label(label, 'state', self._incoming)

        # Add the state.
        self._incoming[label] = []
        self._outgoing[label] = []
        self._is_final[label] = is_final
        self._state_descr[label] = descr
        self._finalizing_string[label] = tuple(finalizing_string)

        # Return the new state's label.
        return label

    def del_state(self, label):
        """
        Delete the state with the given label.  This will
        automatically delete any incoming or outgoing arcs attached to
        the state.
        """
        if label not in self._incoming:
            raise ValueError('Unknown state label %r' % label)

        # Delete the incoming/outgoing arcs.
        for arc in self._incoming[label]:
            del (self._src[arc], self._dst[arc], self._in_string[arc],
                 self._out_string[arc], self._arc_descr[arc])
        for arc in self._outgoing[label]:
            del (self._src[arc], self._dst[arc], self._in_string[arc],
                 self._out_string[arc], self._arc_descr[arc])

        # Delete the state itself.
        del (self._incoming[label], self._otugoing[label],
             self._is_final[label], self._state_descr[label],
             self._finalizing_string[label])

        # Check if we just deleted the initial state.
        if label == self._initial_state:
            self._initial_state = None

    def set_final(self, state, is_final=True):
        """
        If C{is_final} is true, then make the state with the given
        label final; if C{is_final} is false, then make the state with
        the given label non-final.
        """
        if state not in self._incoming:
            raise ValueError('Unknown state label %r' % state)
        self._is_final[state] = is_final

    def set_finalizing_string(self, state, finalizing_string):
        """
        Set the given state's finalizing string.
        """
        if not self._is_final[state]:
            raise ValueError('%s is not a final state' % state)
        if state not in self._incoming:
            raise ValueError('Unknown state label %r' % state)
        self._finalizing_string[state] = tuple(finalizing_string)

    def set_descr(self, state, descr):
        """
        Set the given state's description string.
        """
        if state not in self._incoming:
            raise ValueError('Unknown state label %r' % state)
        self._state_descr[state] = descr

    def dup_state(self, orig_state, label=None):
        """
        Duplicate an existing state.  I.e., create a new state M{s}
        such that:
          - M{s} is final iff C{orig_state} is final.
          - If C{orig_state} is final, then M{s.finalizing_string}
            is copied from C{orig_state}
          - For each outgoing arc from C{orig_state}, M{s} has an
            outgoing arc with the same input string, output
            string, and destination state.

        Note that if C{orig_state} contained self-loop arcs, then the
        corresponding arcs in M{s} will point to C{orig_state} (i.e.,
        they will I{not} be self-loop arcs).

        The state description is I{not} copied.

        @param label: The label for the new state.  If not specified,
            a unique integer will be used.
        """
        if orig_state not in self._incoming:
            raise ValueError('Unknown state label %r' % src)

        # Create a new state.
        new_state = self.add_state(label=label)

        # Copy finalization info.
        if self.is_final(orig_state):
            self.set_final(new_state)
            self.set_finalizing_string(new_state,
                                       self.finalizing_string(orig_state))

        # Copy the outgoing arcs.
        for arc in self._outgoing[orig_state]:
            self.add_arc(src=new_state, dst=self._dst[arc],
                         in_string=self._in_string[arc],
                         out_string=self._out_string[arc])

        return new_state

    #////////////////////////////////////////////////////////////
    #{ Transition Arc Modification
    #////////////////////////////////////////////////////////////

    def add_arc(self, src, dst, in_string, out_string,
                label=None, descr=None):
        """
        Create a new transition arc, and return its label.

        Arguments should be specified using keywords!

        @param src: The label of the source state.
        @param dst: The label of the destination state.
        @param in_string: The input string, a (possibly empty) tuple of
            input symbols.  Input symbols should be hashable
            immutable objects.
        @param out_string: The output string, a (possibly empty) tuple
            of output symbols.  Output symbols should be hashable
            immutable objects.
        """
        label = self._pick_label(label, 'arc', self._src)

        # Check that src/dst are valid labels.
        if src not in self._incoming:
            raise ValueError('Unknown state label %r' % src)
        if dst not in self._incoming:
            raise ValueError('Unknown state label %r' % dst)

        # Add the arc.
        self._src[label] = src
        self._dst[label] = dst
        self._in_string[label] = tuple(in_string)
        self._out_string[label] = tuple(out_string)
        self._arc_descr[label] = descr

        # Link the arc to its src/dst states.
        self._incoming[dst].append(label)
        self._outgoing[src].append(label)

        # Return the new arc's label.
        return label

    def del_arc(self, label):
        """
        Delete the transition arc with the given label.
        """
        if label not in self._src:
            raise ValueError('Unknown arc label %r' % src)

        # Disconnect the arc from its src/dst states.
        self._incoming[self._dst[label]].remove(label)
        self._outgoing[self._src[label]].remove(label)

        # Delete the arc itself.
        del (self._src[label], self._dst[label], self._in_string[label],
             self._out_string[label], self._arc_descr[label])

    #////////////////////////////////////////////////////////////
    #{ Transformations
    #////////////////////////////////////////////////////////////

    def inverted(self):
        """Swap all in_string/out_string pairs."""
        fst = self.copy()
        fst._in_string, fst._out_string = fst._out_string, fst._in_string
        return fst

    def reversed(self):
        """Reverse the direction of all transition arcs."""
        fst = self.copy()
        fst._incoming, fst._outgoing = fst._outgoing, fst._incoming
        fst._src, fst._dst = fst._dst, fst._src
        return fst

    def trimmed(self):
        fst = self.copy()

        if fst.initial_state is None:
            raise ValueError("No initial state!")

        # Determine whether there is a path from the initial node to
        # each node.
        queue = [fst.initial_state]
        path_from_init = set(queue)
        while queue:
            state = queue.pop()
            dsts = [fst.dst(arc) for arc in fst.outgoing(state)]
            queue += [s for s in dsts if s not in path_from_init]
            path_from_init.update(dsts)

        # Determine whether there is a path from each node to a final
        # node.
        queue = [s for s in fst.states() if fst.is_final(s)]
        path_to_final = set(queue)
        while queue:
            state = queue.pop()
            srcs = [fst.src(arc) for arc in fst.incoming(state)]
            queue += [s for s in srcs if s not in path_to_final]
            path_to_final.update(srcs)

        # Delete anything that's not on a path from the initial state
        # to a final state.
        for state in list(fst.states()):
            if not (state in path_from_init and state in path_to_final):
                fst.del_state(state)

        return fst

    def relabeled(self, label=None, relabel_states=True, relabel_arcs=True):
        """
        Return a new FST that is identical to this FST, except that
        all state and arc labels have been replaced with new labels.
        These new labels are consecutive integers, starting with zero.

        @param relabel_states: If false, then don't relabel the states.
        @param relabel_arcs: If false, then don't relabel the arcs.
        """
        if label is None: label = '%s (relabeled)' % self.label
        fst = FST(label)

        # This will ensure that the state relabelling is canonical, *if*
        # the FST is subsequential.
        state_ids = self._relabel_state_ids(self.initial_state, {})
        if len(state_ids) < len(self._outgoing):
            for state in self.states():
                if state not in state_ids:
                    state_ids[state] = len(state_ids)

        # This will ensure that the arc relabelling is canonical, *if*
        # the state labelling is canonical.
        arcs = sorted(self.arcs(), key=self.arc_info)
        arc_ids = dict([(a,i) for (i,a) in enumerate(arcs)])

        for state in self.states():
            if relabel_states: label = state_ids[state]
            else: label = state
            fst.add_state(label, is_final=self.is_final(state),
                          finalizing_string=self.finalizing_string(state),
                          descr=self.state_descr(state))

        for arc in self.arcs():
            if relabel_arcs: label = arc_ids[arc]
            else: label = arc
            src, dst, in_string, out_string = self.arc_info(arc)
            if relabel_states:
                src = state_ids[src]
                dst = state_ids[dst]
            fst.add_arc(src=src, dst=dst, in_string=in_string,
                        out_string=out_string,
                        label=label, descr=self.arc_descr(arc))

        if relabel_states:
            fst.initial_state = state_ids[self.initial_state]
        else:
            fst.initial_state = self.initial_state

        return fst

    def _relabel_state_ids(self, state, ids):
        """
        A helper function for L{relabel()}, which decides which new
        label should be assigned to each state.
        """
        if state in ids: return
        ids[state] = len(ids)
        for arc in sorted(self.outgoing(state),
                          key = lambda a:self.in_string(a)):
            self._relabel_state_ids(self.dst(arc), ids)
        return ids

    def determinized(self, label=None):
        """
        Return a new FST which defines the same mapping as this FST,
        but is determinized.

        The algorithm used is based on [...].

        @require: All arcs in this FST must have exactly one input
            symbol.
        @require: The mapping defined by this FST must be
            deterministic.
        @raise ValueError: If the determinization algorithm was unable
            to determinize this FST.  Typically, this happens because
            a precondition is not met.
        """
        # Check preconditions..
        for arc in self.arcs():
            if len(self.in_string(arc)) != 1:
                raise ValueError("All arcs must have exactly one "
                                 "input symbol.")

        # State labels have the form:
        #   frozenset((s1,w1),(s2,w2),...(sn,wn))
        # Where si is a state and wi is a string of output symbols.
        if label is None: label = '%s (determinized)' % self.label
        new_fst = FST(label)

        initial_state = frozenset( [(self.initial_state,())] )
        new_fst.add_state(initial_state)
        new_fst.initial_state = initial_state

        queue = [initial_state]
        while queue:
            new_fst_state = queue.pop()

            # For each final state from the original FSM that's
            # contained in the new FST's state, compute the finalizing
            # string.  If there is at least one finalizing string,
            # then the new state is a final state.  However, if the
            # finalizing strings are not all identical, then the
            # transduction defined by this FST is nondeterministic, so
            # fail.
            finalizing_strings = [w+self.finalizing_string(s)
                                  for (s,w) in new_fst_state
                                  if self.is_final(s)]
            if len(set(finalizing_strings)) > 0:
                if not self._all_equal(finalizing_strings):
                    # multiple conflicting finalizing strings -> bad!
                    raise ValueError("Determinization failed")
                new_fst.set_final(new_fst_state)
                new_fst.set_finalizing_string(new_fst_state,
                                              finalizing_strings[0])

            # sym -> dst -> [residual]
            # nb: we checked above that len(in_string)==1 for all arcs.
            arc_table = {}
            for (s,w) in new_fst_state:
                for arc in self.outgoing(s):
                    sym = self.in_string(arc)[0]
                    dst = self.dst(arc)
                    residual = w + self.out_string(arc)
                    arc_table.setdefault(sym,{}).setdefault(dst,set())
                    arc_table[sym][dst].add(residual)

            # For each symbol in the arc table, we need to create a
            # single edge in the new FST.  This edge's input string
            # will be the input symbol; its output string will be the
            # shortest common prefix of strings that can be generated
            # by the original FST in response to the symbol; and its
            # destination state will encode the set of states that the
            # original FST can go to when it sees this symbol, paired
            # with the residual output strings that would have been
            # generated by the original FST, but have not yet been
            # generated by the new FST.
            for sym in arc_table:
                for dst in arc_table[sym]:
                    if len(arc_table[sym][dst]) > 1:
                        # two arcs w/ the same src, dst, and insym,
                        # but different residuals -> bad!
                        raise ValueError("Determinization failed")

                # Construct a list of (destination, residual) pairs.
                dst_residual_pairs = [(dst, arc_table[sym][dst].pop())
                                     for dst in arc_table[sym]]

                # Find the longest common prefix of all the residuals.
                # Note that it's ok if some of the residuals disagree,
                # but *only* if the states associated with those
                # residuals can never both reach a final state with a
                # single input string.
                residuals = [res for (dst, res) in dst_residual_pairs]
                prefix = self._common_prefix(residuals)

                # Construct the new arc's destination state.  The new
                # arc's output string will be `prefix`, so the new
                # destination state should be the set of all pairs
                # (dst, residual-prefix).
                new_arc_dst = frozenset([(dst, res[len(prefix):])
                                         for (dst,res) in dst_residual_pairs])

                # If the new arc's destination state isn't part of
                # the FST yet, then add it; and add it to the queue.
                if not new_fst.has_state(new_arc_dst):
                    new_fst.add_state(new_arc_dst)
                    queue.append(new_arc_dst)

                # Create the new arc.
                new_fst.add_arc(src=new_fst_state, dst=new_arc_dst,
                                in_string=(sym,), out_string=prefix)
        return new_fst

    def _all_equal(self, lst):
        """Return true if all elements in the list are equal"""
        for item in lst[1:]:
            if item != lst[0]: return False
        return True

    def _common_prefix(self, sequences):
        """Return the longest sequence that is a prefix of all of the
        given sequences."""
        prefix = sequences[0]
        for seq in sequences[1:]:
            # If the sequence is longer then the prefix, then truncate
            # the prefix to the length of the sequence.
            prefix = prefix[:len(seq)]
            # If the prefix doesn't match item i of the sequence, then
            # truncate the prefix to include everything up to (but not
            # including) element i.
            for i in range(len(prefix)):
                if seq[i] != prefix[i]:
                    prefix = prefix[:i]
                    break
        return prefix

    #////////////////////////////////////////////////////////////
    #{ Misc
    #////////////////////////////////////////////////////////////

    def copy(self, label=None):
        # Choose a label & create the FST.
        if label is None: label = '%s-copy' % self.label
        fst = FST(label)

        # Copy all state:
        fst._initial_state = self._initial_state
        fst._incoming = self._incoming.copy()
        fst._outgoing = self._outgoing.copy()
        fst._is_final = self._is_final.copy()
        fst._finalizing_string = self._finalizing_string.copy()
        fst._state_descr = self._state_descr.copy()
        fst._src = self._src.copy()
        fst._dst = self._dst.copy()
        fst._in_string = self._in_string.copy()
        fst._out_string = self._out_string.copy()
        fst._arc_descr = self._arc_descr.copy()
        return fst

    def __str__(self):
        lines = ['FST %s' % self.label]
        for state in sorted(self.states()):
            # State information.
            if state == self.initial_state:
                line = '-> %s' % state
                lines.append('  %-40s # Initial state' % line)
            if self.is_final(state):
                line = '%s ->' % state
                if self.finalizing_string(state):
                    line += ' [%s]' % ' '.join(self.finalizing_string(state))
                lines.append('  %-40s # Final state' % line)
            # List states that would otherwise not be listed.
            if (state != self.initial_state and not self.is_final(state)
                and not self.outgoing(state) and not self.incoming(state)):
                lines.append('  %-40s # State' % state)
        # Outgoing edge information.
        for arc in sorted(self.arcs()):
            src, dst, in_string, out_string = self.arc_info(arc)
            line = ('%s -> %s [%s:%s]' %
                    (src, dst, ' '.join(in_string), ' '.join(out_string)))
            lines.append('  %-40s # Arc' % line)
        return '\n'.join(lines)

    @staticmethod
    def load(filename):
        label = os.path.split(filename)[-1]
        return FST.parse(label, open(filename).read())

    @staticmethod
    def parse(label, s):
        fst = FST(label)
        prev_src = None
        lines = s.split('\n')[::-1]
        while lines:
            line = lines.pop().split('#')[0].strip() # strip comments
            if not line: continue

            # Initial state
            m = re.match(r'->\s*(\S+)$', line)
            if m:
                label = m.group(1)
                if not fst.has_state(label): fst.add_state(label)
                fst.initial_state = label
                continue

            # Final state
            m = re.match('(\S+)\s*->\s*(?:\[([^\]]*)\])?$', line)
            if m:
                label, finalizing_string = m.groups()
                if not fst.has_state(label): fst.add_state(label)
                fst.set_final(label)
                if finalizing_string is not None:
                    finalizing_string = finalizing_string.split()
                    fst.set_finalizing_string(label, finalizing_string)
                continue

            # State
            m = re.match('(\S+)$', line)
            if m:
                label = m.group(1)
                if not fst.has_state(label): fst.add_state(label)
                continue

            # State description
            m = re.match(r'descr\s+(\S+?):\s*(.*)$', line)
            if m:
                label, descr = m.groups()
                # Allow for multi-line descriptions:
                while lines and re.match(r'\s+\S', lines[-1]):
                    descr = descr.rstrip()+' '+lines.pop().lstrip()
                if not fst.has_state(label): fst.add_state(label)
                fst.set_descr(label, descr)
                continue

            # Transition arc
            m = re.match(r'(\S+)?\s*->\s*(\S+)\s*'
                         r'\[(.*?):(.*?)\]$', line)
            if m:
                src, dst, in_string, out_string = m.groups()
                if src is None: src = prev_src
                if src is None: raise ValueError("bad line: %r" % line)
                prev_src = src
                if not fst.has_state(src): fst.add_state(src)
                if not fst.has_state(dst): fst.add_state(dst)
                in_string = tuple(in_string.split())
                out_string = tuple(out_string.split())
                fst.add_arc(src, dst, in_string, out_string)
                continue

            raise ValueError("bad line: %r" % line)

        return fst

    def dotgraph(self):
        """
        Return an AT&T graphviz dot graph.
        """
        # [xx] mark initial node??
        lines = ['digraph %r {' % self.label,
                 'node [shape=ellipse]']
        state_id = dict([(s,i) for (i,s) in enumerate(self.states())])
        if self.initial_state is not None:
            lines.append('init [shape="plaintext" label=""]')
            lines.append('init -> %s' % state_id[self.initial_state])
        for state in self.states():
            if self.is_final(state):
                final_str = self.finalizing_string(state)
                if len(final_str)>0:
                    lines.append('%s [label="%s\\n%s", shape=doublecircle]' %
                                 (state_id[state], state, ' '.join(final_str)))
                else:
                    lines.append('%s [label="%s", shape=doublecircle]' %
                                 (state_id[state], state))
            else:
                lines.append('%s [label="%s"]' % (state_id[state], state))
        for arc in self.arcs():
            src, dst, in_str, out_str = self.arc_info(arc)
            lines.append('%s -> %s [label="%s:%s"]' %
                         (state_id[src], state_id[dst],
                          ' '.join(in_str), ' '.join(out_str)))
        lines.append('}')
        return '\n'.join(lines)

    #////////////////////////////////////////////////////////////
    #{ Transduction
    #////////////////////////////////////////////////////////////

    def transduce_subsequential(self, input, step=True):
        return self.step_transduce_subsequential(input, step=False).next()[1]

    def step_transduce_subsequential(self, input, step=True):
        """
        This is implemented as a generator, to make it easier to
        support stepping.
        """
        if not self.is_subsequential():
            raise ValueError('FST is not subsequential!')

        # Create a transition table that indicates what action we
        # should take at any state for a given input symbol.  In
        # paritcular, this table maps from (src, in) tuples to
        # (dst, out, arc) tuples.  (arc is only needed in case
        # we want to do stepping.)
        transitions = {}
        for arc in self.arcs():
            src, dst, in_string, out_string = self.arc_info(arc)
            assert len(in_string) == 1
            assert (src, in_string[0]) not in transitions
            transitions[src, in_string[0]] = (dst, out_string, arc)

        output = []
        state = self.initial_state
        try:
            for in_pos, in_sym in enumerate(input):
                (state, out_string, arc) = transitions[state, in_sym]
                if step: yield 'step', (arc, in_pos, output)
                output += out_string
            yield 'succeed', output
        except KeyError:
            yield 'fail', None

    def transduce(self, input):
        return self.step_transduce(input, step=False).next()[1]

    def step_transduce(self, input, step=True):
        """
        This is implemented as a generator, to make it easier to
        support stepping.
        """
        input = tuple(input)
        output = []
        in_pos = 0

        # 'frontier' is a stack used to keep track of which parts of
        # the search space we have yet to examine.  Each element has
        # the form (arc, in_pos, out_pos), and indicates that we
        # should try rolling the input position back to in_pos, the
        # output position back to out_pos, and applying arc.  Note
        # that the order that we check elements in is important, since
        # rolling the output position back involves discarding
        # generated output.
        frontier = []

        # Start in the initial state, and search for a valid
        # transduction path to a final state.
        state = self.initial_state
        while in_pos < len(input) or not self.is_final(state):
            # Get a list of arcs we can possibly take.
            arcs = self.outgoing(state)

            # Add the arcs to our backtracking stack.  (The if condition
            # could be eliminated if I used eliminate_multi_input_arcs;
            # but I'd like to retain the ability to trace what's going on
            # in the FST, as its specified.)
            for arc in arcs:
                in_string = self.in_string(arc)
                if input[in_pos:in_pos+len(in_string)] == in_string:
                    frontier.append( (arc, in_pos, len(output)) )

            # Get the top element of the frontiering stack.
            if len(frontier) == 0:
                yield 'fail', None

            # perform the operation from the top of the frontier.
            arc, in_pos, out_pos = frontier.pop()
            if step:
                yield 'step', (arc, in_pos, output[:out_pos])

            # update our state, input position, & output.
            state = self.dst(arc)
            assert out_pos <= len(output)
            in_pos = in_pos + len(self.in_string(arc))
            output = output[:out_pos]
            output.extend(self.out_string(arc))

        # If it's a subsequential transducer, add the final output for
        # the terminal state.
        output += self.finalizing_string(state)

        yield 'succeed', output


    #////////////////////////////////////////////////////////////
    #{ Helper Functions
    #////////////////////////////////////////////////////////////

    def _pick_label(self, label, typ, used_labels):
        """
        Helper function for L{add_state} and C{add_arc} that chooses a
        label for a new state or arc.
        """
        if label is not None and label in used_labels:
            raise ValueError("%s with label %r already exists" %
                             (typ, label))
        # If no label was specified, pick one.
        if label is not None:
            return label
        else:
            label = 1
            while '%s%d' % (typ[0], label) in used_labels: label += 1
            return '%s%d' % (typ[0], label)

# This function returns fn o ... o f3 o f2 o f1 (input)
# where ALL transducers use characters as input symbols
def composechars(input, *fsts):
    for fst in fsts:
        try:
            input1 = tuple(input)
            input = ''.join(fst.transduce(input1))
        except TypeError:
            sys.stderr.write('Error: One of the FSTs did not produce any output.\n')
            return ''
    return input

# This function returns returns fn o ... o f3 o f2 o f1 (input)
# where transducers use words as input symbols
def composewords(input, *fsts):
    for fst in fsts:
        try:
            input1 = list(input)
            input = fst.transduce(input1)
        except TypeError:
            sys.stderr.write('Error: Could not perform composition.\n')
            return ''
    return ' '.join(input)

# This function allows you to trace the path through
# transducer f with the given input
def trace(f, input):
    input = tuple(input)
    try:
        for step in f.step_transduce(input):
            arc = step[1][0]
            info = f.arc_info(arc)
            input = ''.join(info[2])
            output = ''.join(info[3])
            if not input:
                input = ' '
            if not output:
                output = ' '
            print info[0], '->', info[1], '(', input, ':', output, ')'
    except:
        return
