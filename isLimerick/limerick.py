#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()


    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
        # self.guess_syllables(word)
        cmu = self._pronunciations
        
        vowels = ['A', 'E', 'I', 'O', 'U']
        
        ret_val = float("infinity")

        if word in cmu.keys():
          pro_arr = cmu[word]
          for pro in pro_arr :
            s_syllables = 0
            for s in pro :
              if s[:1] in vowels :
                s_syllables += 1
            if s_syllables < ret_val :
              ret_val = s_syllables
        else:
          ret_val = 1

        return ret_val

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """

        
        cmu = self._pronunciations
        vowels = ['A', 'E', 'I', 'O', 'U']
        # check if a and b present in the dictionary or not
        if a not in cmu.keys():
          return False
        if b not in cmu.keys():
          return False

        pro_arr_a = cmu[a]
        pro_arr_b = cmu[b]

        for index in range(len(pro_arr_a)):
          pro_arr_a[index] = self.normalization(pro_arr_a[index])

        for index in range(len(pro_arr_b)):
          pro_arr_b[index] = self.normalization(pro_arr_b[index])



        for pro_a in pro_arr_a :
          for pro_b in pro_arr_b :
            # TODO : change the length to sounds 
            a_length = len(pro_a)
            b_length = len(pro_b)
            if a_length > b_length:
              smaller_pro = pro_b
              longer_pro = pro_a
            else:
              smaller_pro = pro_a
              longer_pro = pro_b
 
            rhyme_arr = smaller_pro
            len_longer_pro = len(longer_pro)
            i = 0
            
            flag_rhyme = True
            for item in rhyme_arr[::-1]:
              i += 1
              longer_item = longer_pro[len_longer_pro - i]
              # string compare item and  longer_item
              if item != longer_item:
                # does not rhyme 
                flag_rhyme = False
                break;

            if flag_rhyme:
              return True

        return False

    def apostrophe_tokenize(self, line):
      print line
      cmu = self._pronunciations
      words_arr = word_tokenize(line)

      for index in range((len(words_arr)-1),0,-1):
        cur_word = words_arr[index]
        if cur_word not in cmu.keys():
          #combine two words, check in dict
          new_word = words_arr[index-1] + cur_word
          if new_word in cmu.keys():
            words_arr[index] = new_word
            del words_arr[index-1]
            

      return words_arr   


    def normalization(self,pro):
        # find the first consonant. 
        # break after the first vowel sound. 

        # check if all vowels or all consonants 
        # print pro_arr
        vowels = ['A', 'E', 'I', 'O', 'U']
        
        i = 0 
        while (pro[i][:1] not in vowels):
          i += 1
        
        return pro[i:len(pro)]

        


    def guess_syllables(self, word):
      word = word.lower()
      cmu = self._pronunciations
      count = 0
      if word in cmu.keys():
        return self.num_syllables(word)


      vowels = ["a","e","i","o","u","y"]
      index = 0

      while index < len(word):

        while (index < len(word)) and (word[index] not in vowels):
          index += 1
          
        while (index < len(word)) and (word[index] in vowels):
          index += 1

        # now index will have a consonant
        count += 1
        
      return count



    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """

        lines = text.splitlines()

        #removing blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        
        if len(lines) != 5:
          # print len(lines)
          return False

        for k in range(len(lines)) :
          lines[k] = lines[k].lower()
          # lines[k] = re.sub(ur"[^\w\d'\s]+",'',lines[k])
          # lines[k] = self.apostrophe_tokenize(lines[k])
          lines[k] = word_tokenize(lines[k])
          # remove punctuations now
          punc_list = []

          for index in range(len(lines[k])):
            if lines[k][index] in punctuation:
              punc_list.append(index)
            if lines[k][index] == '``':
              punc_list.append(index)

          
          lines[k] = [x for i,x in enumerate(lines[k]) if i not in punc_list]
          # print lines[k]
                
        #check rhyming schema
        flag = self.rhymes(lines[0][-1], lines[1][-1]) and self.rhymes(lines[1][-1], lines[4][-1]) and self.rhymes(lines[2][-1], lines[3][-1]) and (not self.rhymes(lines[1][-1], lines[2][-1])) 
        # print flag
        if flag is False:
          return False

        #checking additional constraints
        # checking A syllables
        syllables = [0,0,0,0,0]
        
        for index in range(len(lines)) :
          for word in lines[index]:
            syllables[index] += self.num_syllables(word)
          
        flag = (abs(syllables[0] - syllables[1]) < 3) and (abs(syllables[4] - syllables[1]) < 3) and (abs(syllables[0] - syllables[4]) < 3) and (abs(syllables[2] - syllables[3]) < 3)
        # print flag
        min_a = min(syllables[0], syllables[1], syllables[4])
        max_b = max(syllables[3], syllables[2])
        min_total = min(min_a, syllables[2], syllables[3])
        
        flag = flag and (max_b < min_a) and (min_total > 3)
        # print flag
        return flag

    


# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')
  
  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
