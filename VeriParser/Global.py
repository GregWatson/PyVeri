# Global object
# used in parsing and run time (simulation)

import sys

class Global(object):

    def __init__(self):
        self.uniq_sigs = {} # dict mapping full UNIQ sig instance name to actual signal
        self.hier_sigs = {} # dict mapping sigs hier name to actual signal
        self.mod_insts = {} # dict mapping module uniq names to their VeriModule objects.
        pass

    def add_signal(self, signal):
        ''' Add the signal to our dict of signals. 
            signal: VeriSignal
        '''
        if signal.uniq_name in self.uniq_sigs:
            print "Error: attempt to add unique signal that was already created:", signal.uniq_name
            sys.exit(1)

        self.uniq_sigs[signal.uniq_name] = signal

        # If the hier_name already exists then this local_named signal is redefined
        # within the module (legal), but need to be careful if it ever gets referenced
        # as a global from some other module because then it's not obvious which one 
        # author is referring to. So set hier_name_is_unique to False if it exists.
        if signal.hier_name in self.hier_sigs:
            self.hier_sigs[signal.hier_name].hier_name_is_unique = False
        else:
            self.hier_sigs[signal.hier_name] = signal



    def add_mod_inst(self, mod_inst):
        ''' Add specified module instance to global list of known module instances.
            mod_inst: VeriModule
        '''
        if mod_inst.full_inst_name in self.mod_insts:
            print "Error: Module instance %s already created." % mod_inst.full_inst_name
            sys.exit(1)
        self.mod_insts[mod_inst.full_inst_name] = mod_inst


    def get_hier_signal(self, hier_name):
        ''' Return the signal referenced by a hierarchical (global) name.
            Sim-time method.
        '''
        sig = self.hier_sigs.get(hier_name, None)
        if not sig:
            print "Error: tried to fetch signal for hier name %s but it was not found in hier sig list." % hier_name
            sys.exit(1)
        return sig

    def get_uniq_signal(self, uniq_name):
        ''' Return the signal referenced by a unique name.
            Sim-time method.
        '''
        sig = self.uniq_sigs.get(uniq_name, None)
        if not sig:
            print "Error: tried to fetch signal for uniq name %s but it was not found in uniq sig list." % uniq_name
            sys.exit(1)
        return sig

    def __str__(self):
        s = "gbl module instances = [\n"
        for m_i in self.mod_insts:
            s += "   " + m_i + "\n"
        s += "]\n"
        s += "gbl sigs=[\n"
        for sig in self.uniq_sigs:
            s += "   " + str(self.uniq_sigs[sig]) + "\n"
        s += "]\n"
        return s
