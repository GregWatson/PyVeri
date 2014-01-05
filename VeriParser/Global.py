# Global object
# used in parsing and run time (simulation)

import sys

class Global(object):

    def __init__(self):
        self.sigs      = {} # dict mapping full UNIQ sig instance name to actual signal
        self.mod_insts = {} # dict mapping module uniq names to their VeriModule objects.
        pass

    def add_signal(self, signal):
        ''' Add the signal to our dict of signals. 
            signal: VeriSignal
        '''
        if signal.uniq_name in self.sigs:
            print "Error: attempt to add unique signal that was already created:", signal.uniq_name
            sys.exit(1)

        self.sigs[signal.uniq_name] = signal


    def add_mod_inst(self, mod_inst):
        ''' Add specified module instance to global list of known module instances.
            mod_inst: VeriModule
        '''
        if mod_inst.full_inst_name in self.mod_insts:
            print "Error: Module instance %s already created." % mod_inst.full_inst_name
            sys.exit(1)
        self.mod_insts[mod_inst.full_inst_name] = mod_inst


    def __str__(self):
        s = "gbl module instances = [\n"
        for m_i in self.mod_insts:
            s += "   " + m_i + "\n"
        s += "]\n"
        s += "gbl sigs=[\n"
        for sig in self.sigs:
            s += "   " + str(self.sigs[sig]) + "\n"
        s += "]\n"
        return s
