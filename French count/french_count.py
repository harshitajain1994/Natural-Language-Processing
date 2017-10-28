import sys
from fst import FST
from fsmutils import composechars, trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

# kFRENCH_TRANS = {1: "un"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    # print list("%03i" % integer)
    return list("%03i" % integer)

def french_count():
    f = FST('french')
    states = ['start', 'final','cent','x','y']
    sub_states = ['cent','x']
    tens = ['a','b','c','d','e','f']

    for state in states :
        f.add_state(state)

    for state in tens :
        f.add_state(state)

    f.initial_state = 'start'
    f.set_final('final')

    #initial zero arcs
    f.add_arc('start', 'x', '0', ())
    f.add_arc('x', 'y', '0', ())
    for i in range(0,10):
        f.add_arc('y', 'final', [str(i)], [kFRENCH_TRANS[i]])

    # start to hundred place arcs
    f.add_arc('start', 'cent', '1', [kFRENCH_TRANS[100]])
    for i in range(2,10) :
        trans = kFRENCH_TRANS[i] + " " + kFRENCH_TRANS[100]
        f.add_arc('start', 'cent', [str(i)], [trans])

    # hundred to tenth place arcs 
    for state in sub_states :
        for ii in xrange(2,7):
            num = ii * 10
            f.add_arc(state, 'a', [str(ii)], [kFRENCH_TRANS[num]])

        f.add_arc(state, 'b', '8', [kFRENCH_TRANS[4]+ " " +kFRENCH_TRANS[20]])
        f.add_arc(state, 'c', '7', [kFRENCH_TRANS[60]])
        f.add_arc(state, 'd', '9', [kFRENCH_TRANS[4]+ " " +kFRENCH_TRANS[20]])
        f.add_arc(state, 'e', '1', ())

    f.add_arc('cent', 'f', '0', ())

    #tenth to ones place arcs
    #adding all empty states
    for state in tens :
        if state != 'e' :
            f.add_arc(state, 'final',(str('0')), ())

    # adding for state a = 2-6
    for i in range(2,10) :
        f.add_arc('a', 'final', [str(i)], [kFRENCH_TRANS[i]])

    num = kFRENCH_AND + " " + kFRENCH_TRANS[1]
    f.add_arc('a', 'final', [str(1)], [num])

    # adding for state c = 7
    num = kFRENCH_AND + " " +kFRENCH_TRANS[11]
    f.add_arc('c', 'final', [str(1)], [num])
    f.add_arc('c', 'final', [str(0)], [kFRENCH_TRANS[10]])
    for i in range(2,7) :
        f.add_arc('c', 'final', [str(i)], [kFRENCH_TRANS[i +10]])
    for i in range(7,10) :
        num = kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[i]
        f.add_arc('c', 'final', [str(i)], [num])


    #adding arcs for b = 8
    for i in range(1,10) :
        f.add_arc('b', 'final', [str(i)], [kFRENCH_TRANS[i]])

    #adding arcs for d = 9
    for i in range(0,7) :
        f.add_arc('d', 'final', [str(i)], [kFRENCH_TRANS[i+10]])
    for i in range(7,10) :
        num = kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[i]
        f.add_arc('d', 'final', [str(i)], [num])

    #adding arcs for e = 1
    for i in range(0,7) :
        f.add_arc('e', 'final', [str(i)], [kFRENCH_TRANS[i+10]])
    for i in range(7,10) :
        num = kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[i]
        f.add_arc('e', 'final', [str(i)], [num])

    #adding arcs for f = 0
    for i in range(1,10) :
        f.add_arc('f', 'final', [str(i)], [kFRENCH_TRANS[i]])

    return f

if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))

    # for user_input in range(250,301) : 
    #     f = french_count()
    #     if string_input:
    #         print " ".join(f.transduce(prepare_input(user_input)))
    #         print user_input
    #         print "\n"

