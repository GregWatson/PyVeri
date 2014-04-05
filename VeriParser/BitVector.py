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
            self.bin_data = val_int & self.mask
            self.is_x = 0
        else:
            self.is_x = self.mask  # all bits are x
        self.num_bits = num_bits

    def copy(self):
        bv = BitVector(self.num_bits, val_int = self.bin_data)
        bv.is_x = self.is_x
        bv.mask = self.mask
        return bv

    def get_bit_range(self, max_bit, min_bit):
        ''' Return a new bv object that is just the specified bits.
            max_bit and min_bit must be less than maximum valid index.
        '''
        bv = self.copy()
        assert(max_bit <= (self.num_bits-1))
        assert(min_bit <= (self.num_bits-1))
        bv.num_bits  = max_bit - min_bit + 1
        bv.mask      = ( 1 << bv.num_bits ) - 1
        bv.bin_data  = (self.bin_data >> min_bit) & bv.mask
        bv.is_x      = (self.is_x     >> min_bit) & bv.mask
        return bv


    def set_num_bits(self, new_num_bits):
        ''' Adjust number of bits as specified. '''
        if self.num_bits == new_num_bits: return

        self.mask     = ( 1 << new_num_bits ) - 1 
        self.num_bits = new_num_bits
        self.bin_data &= self.mask
        self.is_x     &= self.mask

    ## Return current value as an integer.
    # @param self : object
    # @return : Integer.   integer value of bitvector.
    def to_integer(self):
        return self.get_bin_data()

    def get_bin_data(self, self_max=None, self_min=None):
        if self_max==None: return self.bin_data
        # get just the bits needed, shifted down to bit 0.
        mask = ( 1 << (self_max - self_min + 1) ) - 1
        return  (self.bin_data >> self_min) & mask

    def get_is_x(self, self_max=None, self_min=None):
        if self_max==None: return self.is_x
        # get just the bits needed, shifted down to bit 0.
        mask = ( 1 << (self_max - self_min + 1) ) - 1
        return  (self.is_x >> self_min) & mask


    def is_same_when_extended(self, other, self_max=None, self_min=None):
        ''' return bool as to whether self is same as other
            based on only the number of bits in self. 
            #fixme: should sign extend as needed.
            self_max, self_min: set if only using a subset of self's bits
        '''

        self_bin_data = self.get_bin_data(self_max, self_min)
        data_mask = self.mask if self_max == None else ( 1 << (self_max - self_min + 1) ) - 1

        bin_data_same = (self_bin_data & data_mask) == (other.bin_data & data_mask)
        if not bin_data_same: return False

        self_is_x  = self.get_is_x(self_max, self_min)

        if self_max == None:
            x_mask = data_mask if ( self.num_bits <= other.num_bits ) else other.mask
        else:
            num_bits = self_max - self_min + 1
            x_mask = data_mask if ( num_bits <= other.num_bits ) else other.mask

        return (self_is_x & x_mask) == (other.is_x & x_mask)

    
    def update_from(self, other, self_max=None, self_min=None):
        ''' Take only bits from other that are needed to meet self's width.
            Assign to all of self unless self_max (and self_min) are not None.
        '''
        # fixme - sign extend as needed.
        if self_max == None:
            self.bin_data = other.bin_data & self.mask
            self.is_x     = other.is_x     & self.mask
        else:
            # mask is 1 for bits in self that need to be updated
            mask  = ( 1 << (self_max - self_min + 1) ) - 1
            not_mask_shifted = ~(mask << self_min)

            self.bin_data = ( self.bin_data & not_mask_shifted ) | ((other.bin_data & mask ) << self_min)
            self.is_x     = ( self.is_x     & not_mask_shifted ) | ((other.is_x     & mask ) << self_min)


    def bitwise_negate(self): # verilog ~
        ''' Dont change the is_x map: if it's x then it stays x. '''
        self.bin_data ^= self.mask
        return self


    def __cmp__(self, other):

        # dont compare mask
        assert isinstance(other, BitVector) 
        if (    (self.bin_data == other.bin_data) 
              & (self.is_x     == (other.is_x & self.mask))
              & (self.num_bits == other.num_bits)
            ) :
            return 0
        else: 
            return 1


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
                m = self.mask
                d = self.bin_data
                x = self.is_x
                while m:
                    if x & m & 0xf: s = "X" + s
                    else: s = "%x%s" % ((d & m & 0xf), s)
                    d >>= 4
                    x >>= 4
                    m >>= 4
            else:
                s = "%x" % self.bin_data
            s = "%d'h%s" % (self.num_bits, s)
        return s


    def __repr__(self):
        s = 'BitVector( bin_data='  + str(self.bin_data) +   \
                       ' is_x='     + str(self.is_x)     +   \
                       ' num_bits=' + str(self.num_bits) +   \
                       ' mask='     + str(self.mask)     + ')'
        return s
        
