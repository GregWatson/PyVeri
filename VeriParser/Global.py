# Global object
# used in parsing and run time (simulation)

import Code, EventList, VeriModule, VeriTime
import datetime, sys

class Global(object):

    def __init__(self):
        self.uniq_sigs  = {} # dict mapping full UNIQ sig instance name to actual VeriSignal
        self.hier_sigs  = {} # dict mapping sigs hier name to actual VeriSignal
        self.mod_insts  = {} # dict mapping module uniq names to their VeriModule objects.
        self.ev_list    = EventList.EventList() # the event list. Time ordered list of EventsAtOneTime
        self.simCodes   = [] # List of Code.SimCode objects
        self.time       = 0  # current simulation time in fs (used at simulation time)
        self.timescale  = VeriTime.TimeScale() # current timescale
    
        self.debug      = False

        # add a terminating event.
        end_time  = self.ev_list.get_time_of_last_event()
        code = r'   print "Simulation finished at time %d.\n" % gbl.time'
        self.create_and_add_code_to_events(code, end_time,  'inactive_list')


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


    def add_event(self, ev, c_time, list_type):
        ''' Add event to appropriate list within the current list of events.
        '''
        self.ev_list.add_event(ev, c_time, list_type)

    def get_new_simCode_idx(self):
        ''' Create a placeholder in the list of simCodes and return its index. '''
        idx = len(self.simCodes)
        self.simCodes.append(0)
        return idx
    
    def add_simCode(self, simCode):
        idx = simCode.get_index()
        assert ( idx >= 0 and idx < len(self.simCodes))
        self.simCodes[idx] = simCode

    def get_simcode_by_idx(self, idx):
        assert ( idx >= 0 and idx < len(self.simCodes))
        return self.simCodes[idx]

    def execute_simCode_from_idx(self, idx):
        assert ( idx>=0 and idx < len(self.simCodes))
        self.simCodes[idx].fn(self)

    def add_simcode_to_events(self, simcode, c_time, list_type):
        ''' Convenient helper function '''
        ev      = EventList.Event(simcode)
        self.ev_list.add_event(ev, c_time, list_type)

    def create_and_add_code_to_events(self, code, c_time, list_type):
        ''' Convenient helper function '''
        simcode = Code.code_create_uniq_SimCode(self, code)
        self.add_simcode_to_events(simcode, c_time, list_type)


    def get_timescale(self):
        return self.timescale

    def set_current_sim_time(self, time):
        self.time = time

    def run_sim(self, debug=False):
        self.debug = debug
        print "\n------ Simulation Started ------"
        self.sim_start_datetime = datetime.datetime.now()
        self.ev_list.execute(self)


    def process_parse_tree(self, parse_tree):
        ''' Given a parse_tree created by the pyParsing module, go through
            and construct everything we need for a simulation.
        '''
        for el in parse_tree:
            # print "<", el, ">"
            if el[0] == 'module_decl':
                m = VeriModule.VeriModule()
                m.process_element(self, 0, el)
                print m
                print "module scope is ",m.scope
                print self
                continue
            if el[0] == 'timescale':
                self.timescale.process_timescale_spec(scaleL = el[1], precL = el[2])
                print "timescale=",str(self.timescale)
            else:
                print "Dont know how to process",el


    def do_finish(self):
        now = datetime.datetime.now()
        td  = now - self.sim_start_datetime
        
        print "Finished at simulation time", self.time
        print "Executed %d events." % self.ev_list.events_executed
        print "(%d events per second)" % (self.ev_list.events_executed / td.seconds )

    def __str__(self):
        s = "gbl module instances = [\n"
        for m_i in self.mod_insts:
            s += "   " + m_i + "\n"
        s += "]\n"
        s += "gbl sigs=[\n"
        for sig in self.uniq_sigs:
            s += "   " + str(self.uniq_sigs[sig]) + "\n"
        s += "]\n"
        s += "gbl events=[\n" + str(self.ev_list) + "]\n"
        s += "gbl simCodes = [\n"
        for ix,simcode in enumerate(self.simCodes):
            s += "   %d: %s\n" % (ix, simcode.code_text)
        s += "]\n"
        return s