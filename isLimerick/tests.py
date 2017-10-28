import unittest
from limerick import LimerickDetector

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.ld = LimerickDetector()

    def test_rhyme(self):
        s = []
        try: self.assertEqual(self.ld.rhymes("plane", "train"), True)
        except: s.append(1)
        try: self.assertEqual(self.ld.rhymes("eleven", "seven"), True)
        except: s.append(2)
        try: self.assertEqual(self.ld.rhymes("nine", "wine"), True)
        except: s.append(3)
        try: self.assertEqual(self.ld.rhymes("dine", "fine"), True)
        except: s.append(4)
        try: self.assertEqual(self.ld.rhymes("wine", "mine"), True)
        except: s.append(5)
        try: self.assertEqual(self.ld.rhymes("dock", "sock"), True)
        except: s.append(6)
        try: self.assertEqual(self.ld.rhymes("weigh", "fey"), True)
        except: s.append(7)
        try: self.assertEqual(self.ld.rhymes("tree", "debris"), True)
        except: s.append(8)
        try: self.assertEqual(self.ld.rhymes("niece", "peace"), True)
        except: s.append(9)
        try: self.assertEqual(self.ld.rhymes("read", "need"), True)
        except: s.append(10)
        try: self.assertEqual(self.ld.rhymes("dog", "cat"), False)
        except: s.append(11)
        try: self.assertEqual(self.ld.rhymes("bagel", "sail"), False)
        except: s.append(12)
        try: self.assertEqual(self.ld.rhymes("wine", "rind"), False)
        except: s.append(13)
        try: self.assertEqual(self.ld.rhymes("failure", "savior"), False)
        except: s.append(14)
        try: self.assertEqual(self.ld.rhymes("fly", "butterfly"), False)
        except: s.append(15)
        try: self.assertEqual(self.ld.rhymes("cyst", "fist"), True)
        except: s.append(16)
        try: self.assertEqual(self.ld.rhymes("gist", "grist"), True)
        except: s.append(17)
        try: self.assertEqual(self.ld.rhymes("kissed", "list"), True)
        except: s.append(19)
        try: self.assertEqual(self.ld.rhymes("liszt", "missed"), True)
        except: s.append(20)
        try: self.assertEqual(self.ld.rhymes("mist", "tryst"), True)
        except: s.append(21)
        


        print '\nNumber of failed rhyme tests:', str(len(s))
        if len(s)!=0: print 'Failed rhyme tests:', ','.join([str(x) for x in s])

    def test_syllables(self):
        s = []
        try: self.assertEqual(self.ld.num_syllables("ninety"), 2)
        except: s.append(1)
        try: self.assertEqual(self.ld.num_syllables("university"), 5)
        except: s.append(2)
        try: self.assertEqual(self.ld.num_syllables("letter"), 2)
        except: s.append(3)
        try: self.assertEqual(self.ld.num_syllables("washington"), 3)
        except: s.append(4)
        try: self.assertEqual(self.ld.num_syllables("dock"), 1)
        except: s.append(5)
        try: self.assertEqual(self.ld.num_syllables("dangle"), 2)
        except: s.append(6)
        try: self.assertEqual(self.ld.num_syllables("thrive"), 1)
        except: s.append(7)
        try: self.assertEqual(self.ld.num_syllables("fly"), 1)
        except: s.append(8)
        try: self.assertEqual(self.ld.num_syllables("placate"), 2)
        except: s.append(9)
        try: self.assertEqual(self.ld.num_syllables("renege"), 2)
        except: s.append(10)
        try: self.assertEqual(self.ld.num_syllables("reluctant"), 3)
        except: s.append(11)

        print '\nNumber of failed syllables tests:', str(len(s))
        if len(s)!=0: print 'Failed syllables tests:', ','.join([str(x) for x in s])

    def test_examples(self):

        a = """
a woman whose friends called a prude
on a lark when bathing all nude
saw a man come along
and unless we are wrong
you expected this line to be lewd
        """

        b = """while it's true all i've done is delay
in defense of myself i must say
today's payoff is great
while the workers all wait
"""

        c = """
this thing is supposed to rhyme
but I simply don't got the time
who cares if i miss,
nobody will read this
i'll end this here poem potato
"""

        d = """There was a young man named Wyatt
whose voice was exceedingly quiet
And then one day
it faded away"""

        e = """An exceedingly fat friend of mine,
When asked at what hour he'd dine,
Replied, ' "At eleven,     
At three, five, and seven,
And eight and a quarter past nine"""

        f = """A limerick fan from Australia
regarded his work as a failure:
his verses were fine
until the fourth line"""

        g = """There was a young lady one fall
Who wore a newspaper dress to a ball.
The dress caught fire
And burned her entire
Front page, sporting section and all."""

        h = "dog\ndog\ndog\ndog\ndog"

        ab = """A wonderful bird is the pelican,

        His bill can hold more than his beli-can.

        He can take in his beak

        Food enough for a week

        But I'm damned if I see how the heli-can."""

        ac = """The limerick packs laughs anatomical
                Into space that is quite economical.
                But the good ones I've seen 
                So seldom are clean
                And the clean ones so seldom are comical"""

        ad = """There once was a son of a duke
        Whose upbringing was really a fluke:
        He was raised by some gibbons
        With apes for his siblin's
        So all he can say now is "ook." """

        ae = """May you purge all the lust from my soul,

        Give me continence and self-control,

        Give me patience and love

        From the heavens above

        To obey your commands in their whole."""

        af = """Our novels get longa and long

        Their language gets stronga and strong

        There is much to be said

        For the life that is led

        In illiterate places like Bong"""

        ag = """With the ladies I'm not a chart-topper

        I seem dainty and meek and a flopper

        I'll be more of a chief

        If I smell like cooked beef

        With the scent of a Burger King Whopper"""

        p="""There was a Young Person of Crete,
Whose toilette was far from complete;
She dressed in a sack,
Spickle-speckled with black,
That ombliferous person of Crete."""

        t="""Can't believe it's true, must be a ruse.
It seems kids these days actually choose.
It's a very strange fad,
to dress up just like Dad.
Bell-bottom pants and big clunky shoes."""
        u="""There was an old man from Peru
Who dreamt he was eating his shoe.
He awoke in a fright
In the middle of the night
And found it was perfectly true"""

        s = []

        try: self.assertEqual(self.ld.is_limerick(a), True)
        except: s.append('a')
        try: self.assertEqual(self.ld.is_limerick(b), False)
        except: s.append('b')
        try: self.assertEqual(self.ld.is_limerick(c), False)
        except: s.append('c')
        try: self.assertEqual(self.ld.is_limerick(d), False)
        except: s.append('d')
        try: self.assertEqual(self.ld.is_limerick(f), False)
        except: s.append('f')
        try: self.assertEqual(self.ld.is_limerick(u), True)
        except: s.append('u')
        try: self.assertEqual(self.ld.is_limerick(g), True)
        except: s.append('g')
        try: self.assertEqual(self.ld.is_limerick(aa), True)
        except: s.append('aa')
        try: self.assertEqual(self.ld.is_limerick(ab), True)
        except: s.append('ab')
        try: self.assertEqual(self.ld.is_limerick(ac), True)
        except: s.append('ac')
        try: self.assertEqual(self.ld.is_limerick(ad), True)
        except: s.append('ad')
        try: self.assertEqual(self.ld.is_limerick(ae), True)
        except: s.append('ae')
        try: self.assertEqual(self.ld.is_limerick(af), True)
        except: s.append('af')
        try: self.assertEqual(self.ld.is_limerick(ag), True)
        except: s.append('ag')
        try: self.assertEqual(self.ld.is_limerick(p), True)
        except: s.append('p')
        try: self.assertEqual(self.ld.is_limerick(t), True)
        except: s.append('t')
        try: self.assertEqual(self.ld.is_limerick(u), True)
        except: s.append('u')

        print 'Number of failed limerick tests:', str(len(s))
        if len(s)!=0: print 'Failed limerick tests:', ','.join(s)

if __name__ == '__main__':
    unittest.main()
