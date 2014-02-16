# Verilog signal, wire and register types.

import BitVector
import sys

class VeriSignal(object):    # base class for comb_gate and seq_gate

    _uniq_num = 0 # used to assign unique names to signals

    
    @classmethod
    def reset_uniq_number(cls):
        VeriSignal._uniq_num = 0

    @classmethod
    def get_next_uniq_num(cls):
        VeriSignal._uniq_num += 1
        return VeriSignal._uniq_num


    # signal uniq name is the full module instance name plus the local name plus a
    # unique integer.  e.g. top.a1.b1.mod3.adder_5
    def __init__(self, mod_inst_name = '', **kwargs):
        self.sig_type   = None # should be 'reg' or 'net'
        self.local_name = ''  # simple name within a module.
        self.uniq_name  = ''  # global uniq name used in gbl structure( mod_inst_name + '.' uniq)
        self.hier_name  = ''  # hierarchical name: mod_inst_name + '.' + local_name
        self.hier_name_is_unique = True # if this is only signal in module with this local_name
        self.is_signed  = False
        self.vec_min    = 0   # index ranges for simple register or wire
        self.vec_max    = 0
        for (attr, val) in kwargs.iteritems():
            if attr in self.__dict__:
                print "reg : set attr %s to %s" % ( attr, val)
                setattr(self, attr, val)
                if attr == 'local_name': 
                    self.uniq_name = mod_inst_name + '.' + val + '_' + str(VeriSignal.get_next_uniq_num())
                    self.hier_name = mod_inst_name + '.' + val
            else:
                print "VeriSignal.__init__: Internal error: unknown attribute '%s' in signal object." % attr
                sys.exit(1)

        print "reg",self.hier_name,"is",self.vec_max - self.vec_min + 1,"bits wide."
        self.bit_vec    = BitVector.BitVector(self.vec_max - self.vec_min + 1)

        if self.sig_type == None:
            print "Internal Error: VeriSignal.VeriSignal(): self.sig_type not specified when signal %s created!" % self.hier_name
            sys.exit(1)



    def get_value(self):
        return self.bit_vec

    def set_value(self, bv):
        ''' set self.bit_vec to the given bv.
            But must adjust width appropriately. '''
        bv.set_num_bits(self.bit_vec.num_bits)
        self.bit_vec = bv

    def __str__(self):
        s = self.local_name + "(%s)" % self.uniq_name
        if self.is_signed: s += ' (signed) '
        if self.vec_max > 0:
            s += " [%d:%d] " % ( self.vec_max, self.vec_min )
        if self.bit_vec:
            s += str(self.bit_vec)
        else: s += '(value undefined)'
        return s
