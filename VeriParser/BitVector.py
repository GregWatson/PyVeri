##############################################
#
# Module BitVector.py
#
##############################################

class BitVector(object):

    def __init__(self, num_bits, val_int=None):
        ''' Create a BitVector of num_bits bits. 
            val_str is initial value as a string (binary, hex etc)
            val_int is initial value as an integer.
            Note that we store two bits for each simulated bit, and these are stored in two arrays: 

            self.bin_data is int that holds the raw data for the bits if they are 0 or 1.
            self.is_x     is set to 1 if the bit is X (unknown).
            self.num_bits is number of bits
            self.mask     is a bit mask (all 1s) of num_bits
        '''
        self.mask = ( 1 << num_bits ) - 1  # e.g. num_bits =3 then mask = 000....0111
        self.bin_data = 0

        if val_int != None:   # This is a hack to just get things going. fixme
            self.bin_data = val_int
            self.is_x = 0
        else:
            self.is_x = self.mask  # all bits are x
        self.num_bits = num_bits

    def set_num_bits(self, new_num_bits):
        ''' Adjust number of bits as specified. '''
        if self.num_bits == new_num_bits: return

        self.mask     = ( 1 << new_num_bits ) - 1 
        self.num_bits = new_num_bits
        self.bin_data &= self.mask
        self.is_x     &= self.mask

    def is_same_when_extended(self, other):
        ''' return bool as to whether self is same as other
            based on only the number of bits in self. 
            #fixme: should sign extend as needed.
        '''
        bin_data_same = (self.bin_data & self.mask) == (other.bin_data & self.mask)
        if not bin_data_same: return False
        return (self.is_x & self.mask) == (other.is_x & self.mask)

    
    def update_from(self, other):
        ''' Take only bits from other that are needed to meet self's width '''
        # fixme - sign extend as needed.
        self.bin_data = other.bin_data & self.mask
        self.is_x     = other.is_x     & self.mask
        

    def bitwise_negate(self): # verilog ~
        ''' Dont change the is_x map: if it's x then it stays x. '''
        self.bin_data ^= self.mask
        return self

    def __add__(self, other): # add two integers together
        ''' fixme - need to add signed behavior '''

        num_bits     = max(self.num_bits, other.num_bits)
        mask         = max(self.mask,     other.mask)
        unsigned_sum = self.bin_data + other.bin_data

        result   = BitVector( num_bits, val_int = unsigned_sum & mask )
        result.mask = mask
        result.is_x = self.is_x | other.is_x  # fixme. WRONG: all bits above 1st x are x.
        return result
            
        
    def __str__(self,mode='x'):
        s = ''
        if mode=='x':  #fixme. this is too simple.
            if self.is_x: 
                s = 'X' * ((self.num_bits + 3)/4)
            else:
                s = "%x" % self.bin_data
        return s


    def __repr__(self):
        s = 'BitVector( bin_data='  + str(self.bin_data) +   \
                       ' is_x='     + str(self.is_x)     +   \
                       ' num_bits=' + str(self.num_bits) +   \
                       ' mask='     + str(self.mask)     + ')'
        return s
        
