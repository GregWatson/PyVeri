##############################################
#
# Module BitVector.py
#
##############################################

from array import *

class BitVector(object):

    def __init__(self, num_bits, val_str='', val_int=None):
        ''' Create a BitVector of num_bits bits. 
            val_str is initial value as a string (binary, hex etc)
            val_int is initial value as an integer.
            Note that we store two bits for each simulated bit, and these are stored in two arrays: 
            self.bin_data[] holds the raw data for the bits if they are 0 or 1.
            self.is_x[] is set to 1 if the bit is X (unknown).
            least sig data is in index 0

            self.mask is a bit mask for use on final array entry (which might not be 32 bits) 
            self.num_words is number of base type words used in array (i.e. len(array))
            self.num_bits is number of bits
        '''
        bin_data = array('L')
        is_x     = array('L')
        
        bits_per_word = bin_data.itemsize*8  
        num_words_needed = int((num_bits-1)/bits_per_word)+1
        self.num_words = num_words_needed
        # print "Need",num_bits,"bits. Bits_per_word is ", bits_per_word," need",num_words_needed,"words."
        while (num_words_needed > 1):
            bin_data.append(0)
            is_x.append(0xffffffff)
        if num_bits == 32: self.mask = 0xffffffff
        else: self.mask = ( 1 << (num_bits % 32) ) - 1  # e.g. num_bits =3 then mask = 000....0111
        if val_int != None:   # This is a hack to just get things going. fixme
            bin_data.append(val_int)  # fixme
            is_x.append(0)
        else:
            bin_data.append(0) 
            is_x.append(self.mask)

        self.bin_data = bin_data
        self.is_x     = is_x
        self.num_bits = num_bits

    
    def bitwise_negate(self): # verilog ~
        ''' Dont change the is_x map: if it's x then it stays x. '''
        self.bin_data = map(lambda t: t ^ 0xffffffff, self.bin_data)
        self.bin_data[-1] = self.bin_data[-1] & self.mask
        return self

    def __add__(self, other): # add two integers together
        ''' fixme - need to add signed behavior '''
        wider = self
        shorter = other
        if other.num_bits > wider.num_bits: 
            wider = other
            shorter = self
        result = BitVector( wider.num_bits )
        carry = 0
        for ix in xrange(wider.num_words):
            shorter_num = 0
            is_x = wider.is_x[ix]
            if ix < shorter.num_words:
                shorter_num = shorter.bin_data[ix]
                is_x = is_x | shorter.is_x[ix]

            word_result = wider.bin_data[ix] + shorter_num + carry
            result.bin_data[ix] = word_result & 0xffffffffL
            carry = word_result >> 32

            result.is_x[ix] = is_x

        result.bin_data[-1] &= result.mask
        return result
            
        
    def __str__(self,mode='x'):
        s = ''
        if mode=='x':  #fixme. this is too simple.
            for ix in xrange(self.num_words):
                if self.is_x[ix]: 
                    s = 'XXXXXXXX' + s
                else:
                    s = "%08x" % self.bin_data[ix] + s
        return s
            
        
            
