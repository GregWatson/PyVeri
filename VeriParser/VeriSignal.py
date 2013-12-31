# Verilog signal, wire and register types.

import sys

class VeriSignal(object):    # base class for comb_gate and seq_gate

    def __init__(self):
        self.local_name = ''  # simple name within a module.
        self.full_name  = ''  # full hierarchical name.
        self.is_signed  = False
        self.vec_min    = 0   # index ranges for simple register or wire
        self.vec_max    = 0




class seq_gate(VeriSignal):

    def __init__(self, **kwargs):
        super(seq_gate, self).__init__()
        for (attr, val) in kwargs.iteritems():
            if attr in self.__dict__:
                setattr(self, attr, val)
            else:
                print "Internal error: unknown attribute '%s' in seq_gate object." % attr
                sys.exit(1)

        
    def to_string(self):
        s = self.local_name
        if self.is_signed: s += ' (signed) '
        if self.vec_max > 0:
            s += " [%d:%d]" % ( self.vec_max, self.vec_min )
        return s
