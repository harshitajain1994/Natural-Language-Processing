from fst import FST
import string, sys
from fsmutils import composechars, trace

def letters_to_numbers():
    """
    Returns an FST that converts letters to numbers as specified by
    the soundex algorithm
    """

    # Let's define our first FST
    f1 = FST('soundex-generate')
    letter_groups = [['b','f','p','v','B','F','P','V'],['c','C', 'g','G','J', 'j', 'K','k','Q', 'q','S', 's','X', 'x', 'Z','z'],['d','D','T','t'],['L','l'],['M','N','m','n'],['R','r']]
    vowels = ['a','e','i','o','u','w','y','h','A','E','I','O','U','W','Y','H']
    states_num = len(letter_groups)
    
    f1.add_state('start')
    f1.add_state('vowels')
    f1.set_final('vowels')
    for i in range(states_num) :
        f1.add_state(i)
        f1.set_final(i)

    f1.initial_state = 'start'

    # Add the rest of the arcs
    # f1.add_arc('vowels','start',(),())

    for letter in string.ascii_letters:
        if letter in vowels :
            f1.add_arc('start','vowels',(letter),(letter)) #first char is vowel
            f1.add_arc('vowels','vowels',(letter),()) #ignoring consecutive vowels iin start
            for i in range(states_num) :
                f1.add_arc(i,'vowels',(letter),())

        else :
            for conso_state in range(states_num):
                if letter in letter_groups[conso_state] :
                    f1.add_arc('start',conso_state,(letter),(letter))
                    f1.add_arc('vowels',conso_state,(letter),(str(conso_state+1)[0]))
                    f1.add_arc(conso_state,conso_state,(letter),())
                    for other_conso_state in range(states_num):
                        if other_conso_state != conso_state :
                            f1.add_arc(other_conso_state,conso_state,(letter),(str(conso_state+1)[0]))


    return f1

    # The stub code above converts all letters except the first into '0'.
    # How can you change it to do the right conversion?

def truncate_to_three_digits():
    """
    Create an FST that will truncate a soundex string to three digits
    """

    # Ok so now let's do the second FST, the one that will truncate
    # the number of digits to 3
    f2 = FST('soundex-truncate')


    # Indicate initial and final states
    f2.add_state('start')
    for i in range(4):
        # print i
        f2.add_state(i)
        f2.set_final(i)

    
    f2.initial_state = 'start'
    

    # # Add the arcs
    for letter in string.letters:
        f2.add_arc('start', 0, (letter), (letter))

    for n in range(10):
        f2.add_arc('start', 1, (str(n)), (str(n)))
        for i in range(3) :
            f2.add_arc(i, i+1, (str(n)), (str(n)))

        f2.add_arc(3,3,(str(n)),())

    # trace(f2,'2345')

    # return f2
    # trace(f2,'2345')
    return f2





    # The above stub code doesn't do any truncating at all -- it passes letter and number input through
    # what changes would make it truncate digits to 3?

def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    f3.add_state('start')
    # f3.add_state('1a')
    # f3.add_state('1b')
    # f3.add_state('2')

    for i in range(7) :
        f3.add_state(i)
    
    f3.initial_state = 'start'
    f3.set_final(3)
    f3.set_final(6)

    for letter in string.letters:
        f3.add_arc('start', 0, (letter), (letter))

    for number in xrange(10):
        f3.add_arc('start', 1, (str(number)), (str(number)))
        for i in range(3) :
            f3.add_arc(i, i+1, (str(number)), (str(number)))
    
    # f3.add_arc('1', '1a', (), ('0'))
    # f3.add_arc('1a', '1b', (), ('0'))
    # f3.add_arc('1b', '2', (), ('0'))

    # adding empty number arcs :

    for i in range(3) :
        f3.add_arc(i, i+4, (), ('0'))

    for i in range(4,6) :
        f3.add_arc(i, i+1, (), ('0'))

    # trace(f3,'A5')

    return f3

    # The above code adds zeroes but doesn't have any padding logic. Add some!

if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))
