# Verilog signal, wire and register types.

import BitVector
import sys

class VeriSignal(object):    # base class for comb_gate and seq_gate

    _uniq_num = 0 # used to assign unique names to signals

    @classmethod
    def get_next_uniq_num(cls):
        VeriSignal._uniq_num += 1
        return VeriSignal._uniq_num


    def __init__(self):
        self.local_name = ''  # simple name within a module.
        self.uniq_name  = ''  # unique name
        self.is_signed  = False
        self.vec_min    = 0   # index ranges for simple register or wire
        self.vec_max    = 0
        self.bit_vec    = None

    def initialize(self):
        ''' set to undefined value e.g. at start of simulation '''
        num_bits = self.vec_max - self.vec_min + 1
        self.bit_vec = BitVector.BitVector(num_bits)
        # print "bit_vec is ",self.bit_vec



class seq_gate(VeriSignal):

    def __init__(self, **kwargs):
        super(seq_gate, self).__init__()
        for (attr, val) in kwargs.iteritems():
            if attr in self.__dict__:
                setattr(self, attr, val)
                if attr=='local_name': 
                    self.uniq_name = val + '_' + str(VeriSignal.get_next_uniq_num())
            else:
                print "Internal error: unknown attribute '%s' in seq_gate object." % attr
                sys.exit(1)

        
    def __str__(self):
        s = self.local_name + "(%s)" % self.uniq_name
        if self.is_signed: s += ' (signed) '
        if self.vec_max > 0:
            s += " [%d:%d] " % ( self.vec_max, self.vec_min )
        if self.bit_vec:
            s += str(self.bit_vec)
        else: s += '(value undefined)'
        return s