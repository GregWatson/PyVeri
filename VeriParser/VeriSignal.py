# Verilog signal, wire and register types.

import BitVector, Code, VeriExceptions
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
        self.local_name = ''  # simple name within a module.
        self.uniq_name  = ''  # global uniq name used in gbl structure( mod_inst_name + '.' uniq)
        self.hier_name  = ''  # hierarchical name: mod_inst_name + '.' + local_name
        self.hier_name_is_unique = True # if this is only signal in module with this local_name
        self.sig_type   = None # should be 'reg' or 'net'
        self.is_port    = False
        self.port_dir   = None # 'in' or 'out' or 'inout'
        self.is_signed  = False
        self.vec_min    = 0   # index ranges for simple register or wire
        self.vec_max    = 0
        self.dependent_simcodes = [] # when self changes then recompute signals in this list.
        self.bit_vec = None
        self.last_update_time = 0  # used for runtime loop detection.
        self.same_time_count  = 0  # used for runtime loop detection.
        
        for (attr, val) in kwargs.iteritems():
            if attr in self.__dict__:
                # print "reg : set attr %s to %s" % ( attr, val)
                setattr(self, attr, val)
                if attr == 'local_name': 
                    self.uniq_name = mod_inst_name + '.' + val + '_' + str(VeriSignal.get_next_uniq_num())
                    self.hier_name = mod_inst_name + '.' + val
            else:
                print "VeriSignal.__init__: Internal error: unknown attribute '%s' in signal object." % attr
                sys.exit(1)

        # print "reg",self.hier_name,"is",self.vec_max - self.vec_min + 1,"bits wide."

        self.bit_vec = BitVector.BitVector( self.vec_max - self.vec_min + 1 )

        if self.sig_type == None:
            print "Internal Error: VeriSignal.VeriSignal(): self.sig_type not specified when signal %s created!" % self.hier_name
            sys.exit(1)



    def get_value(self):
        return self.bit_vec.copy()



    def set_value(self, bv, self_max=None, self_min=None, bv_max=None, bv_min=None):
        ''' set self.bit_vec to the given bv.
            self_max: m.s.b of self to be set (or None if all of self)
            self_min: l.s.b of self to be set (or None if all of self)
            bv_max: m.s.b of bv to be used ( None means all)
            bv_min: l.s.b of bv to be used ( None means all)
            But allow for differing widths (zero extend) #fixme - sign extend really.
            If we actually change self then we must process the dependent_simcodes list.
        '''
        global gbl

        # print "set_value self=",`self.bit_vec`,"\n\t    bv=",`bv`
        if bv_max != None:
            bv = bv.get_bit_range(bv_max, bv_min)        

        # compute how many bits of self we are going to set.
        num_bits_to_set = self.bit_vec.num_bits

        if self_max == None:  # Common case: not assigning subset of bits.
            self_max = self.vec_max
            self_min = self.vec_min

            if num_bits_to_set == bv.num_bits:
                if self.bit_vec == bv: 
                    # print "bit vector", self,"not changing - not updating it."
                    return
            else:
                if self.bit_vec.is_same_when_extended(bv):
                    # print "bit vector", self,"not changing - not updating it."
                    return


        else: # assigning subset of bits.

            num_bits_to_set = self_max - self_min + 1
            assert num_bits_to_set <= self.bit_vec.num_bits,"Assigning too many bits to "+self.uniq_name
            if self.bit_vec.is_same_when_extended(bv, self_max, self_min):
                # print "bit vector ", self, "bits", self_max, self_min,"are same as\n\t",bv," so not updating it."
                return

        # <GREG add monitoring of signals>

        print "Updating signal",self.hier_name,"\n\t was:",self.bit_vec
        self.bit_vec.update_from(bv, self_max, self_min)
        print "\t new:",self.bit_vec


        if self.dependent_simcodes: 
            self.process_dependent_simcodes()


    def add_dependent_simcode(self, simcode):
        if simcode not in self.dependent_simcodes:
            self.dependent_simcodes.append(simcode)


    def process_dependent_simcodes(self):
        ''' Recompute all dependent signals. '''
        # print "Recomputing sigs dependent on",self.hier_name
        gbl = Code.SimCode.gbl

        #check for infinite loops.
        if gbl.time == self.last_update_time:
            self.same_time_count += 1
            if  self.same_time_count >= gbl.update_loop_detect_thresh:
                print "ERROR: run time loop detection threshold (", \
                       gbl.update_loop_detect_thresh, ") exceeded for signal", self.hier_name
                gbl.do_finish()
                raise VeriExceptions.RuntimeInfiniteLoopError, self.hier_name
        else:
            self.last_update_time = gbl.time
            self.same_time_count  = 1
        

        for simcode in self.dependent_simcodes:
            # print "Adding simcode", simcode.get_index(),"to events at time", gbl.time
            gbl.add_simcode_to_events(simcode, gbl.time, 'active_list')



    def __str__(self):
        s = self.sig_type + ' ' + self.local_name + "(%s)" % self.uniq_name
        if self.is_signed: s += ' (signed) '
        if self.vec_max > 0:
            s += " [%d:%d] " % ( self.vec_max, self.vec_min )
        if self.bit_vec:
            s += str(self.bit_vec)
        else: s += '(value undefined)'
        if self.is_port: 
            s += ' port:' + self.port_dir
        return s
