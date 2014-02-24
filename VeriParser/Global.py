# Global object
# used in parsing and run time (simulation)

import Code, EventList, VeriTime, VeriSignal
import datetime, sys

class Global(object):

    DBG_STATS      = 1<<1
    DBG_EVENT_LIST = 1<<2

    def __init__(self, sim_end_time_fs=0xfffffffL , debug=0):

        self.sim_end_time_fs = sim_end_time_fs  # when sim MUST end

        self.uniq_sigs  = {} # dict mapping full UNIQ sig instance name to actual VeriSignal
        self.hier_sigs  = {} # dict mapping sigs hier name to actual VeriSignal
        self.mod_insts  = {} # dict mapping module uniq names to their VeriModule objects.
        self.ev_list    = EventList.EventList(self.sim_end_time_fs) # the event list. Time ordered list of EventsAtOneTime
        self.simCodes   = [] # List of Code.SimCode objects
        self.time       = 0  # current simulation time in fs (used at simulation time)
        self.debug      = debug

        # if sig gets updated more often than this in same simulation
        # time cycle then we declare a loop and exit.
        self.update_loop_detect_thresh = 1000 



        # add a terminating event.
        end_time  = self.ev_list.get_time_of_last_event()
        code  = r'   print "Simulation finished at time %d.\n" % gbl.time'
        code +=  '\n   return None\n'
        self.create_and_add_code_to_events(code, end_time,  'inactive_list')

        #restart signal numbering at 0
        VeriSignal.VeriSignal.reset_uniq_number()


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
        # the author is referring to. So set hier_name_is_unique to False if it exists.
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
        if self.debug & Global.DBG_EVENT_LIST :
            print "DBG: [%d] %s" % (self.time, self.simCodes[idx].code_text)

        return self.simCodes[idx].fn(self)

    def add_simcode_to_events(self, simcode, c_time, list_type):
        ''' Convenient helper function '''
        ev      = EventList.Event(simcode)
        self.ev_list.add_event(ev, c_time, list_type)

    def create_and_add_code_to_events(self, code, c_time, list_type):
        ''' Convenient helper function '''
        simcode = Code.code_create_uniq_SimCode(self, code)
        self.add_simcode_to_events(simcode, c_time, list_type)
        return simcode

    def get_timescale(self):
        return self.timescale

    def set_current_sim_time(self, time):
        self.time = time

    def run_sim(self, debug=0):
        self.debug = debug
        Code.SimCode.gbl = self
        print "\n------ Simulation Started ------"
        self.sim_start_datetime = datetime.datetime.now()
        self.ev_list.execute(self)


    def do_finish(self):
        now = datetime.datetime.now()
        td  = now - self.sim_start_datetime
        
        if self.debug & Global.DBG_STATS: 
            print "Finished at simulation time", self.time
            print "Executed %d events in  %d seconds." % (self.ev_list.events_executed, td.seconds)
            if td.seconds: print "(%d events per second)" % (self.ev_list.events_executed / td.seconds )

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
