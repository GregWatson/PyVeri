##############################################
#
# Module EventList.py
#
##############################################

import Global

_next_uniq_fn = 0

def get_uniq_fn_name(base_name):
    ''' return a unique function name given a base name '''
    _next_uniq_fn += 1
    return "%s_%d" % (base_name, _next_uniq_fn)

class Event(object):
    ''' Single event in the event list '''
    
    def __init__(self, simcode=None):
        self.simcode  = simcode  # simcode.fn = is function f(gbl)



''' Event list is a time (number) ordered list of Event.
    For any given event time with at least one Event there are 
    several lists corresponding to the Verilog Simulation Model.
    
    Each list is processed in this order.

    1) Events that occur at the current simulation time and can be processed 
       in any order. These are the active events.
    2) Events that occur at the current simulation time, but that shall be 
       processed after all the active events are processed. These are the inactive events.
    3) Events that have been evaluated during some previous simulation time, 
       but that shall be assigned at this simulation time after all the active 
       and inactive events are processed. These are the non blocking assign update events.
    4) Events that shall be processed after all the active, inactive, and non blocking 
       assign update events are processed. These are the monitor events.
'''

class EventsAtOneTime(object):
    ''' This has the various lists of events that all occur at a given time '''

    def __init__(self,time):
        self.time = time
        self.active_list      = []
        self.inactive_list    = []
        self.nonblocking_list = []
        self.monitor_list     = []

    def add_event(self, event, list_type):
        ''' Add the event object to the specified list '''
        method = 'add_event_to_' + list_type
        getattr(self, method)(event)

    def add_event_to_active_list     (self, event): self.active_list.append(event)
    def add_event_to_inactive_list   (self, event): self.inactive_list.append(event)
    def add_event_to_nonblocking_list(self, event): self.nonblocking_list.append(event)
    def add_event_to_monitor_list    (self, event): self.monitor_list.append(event)

    def get_num_all_events(self):
        return len(self.active_list)      + len(self.inactive_list) + \
               len(self.nonblocking_list) + len(self.monitor_list)

    def execute_list(self, gbl, main_ev_list, ev_list):
        ''' execute all events on current list '''
        while len(ev_list):
            event = ev_list[0]
            if gbl.debug & Global.Global.DBG_EVENT_LIST: print "[%d] execute:<%s>" % (self.time, event.simcode.code_text)
            nxt_simCode_idx = gbl.execute_simCode_from_idx(event.simcode.get_index())
            while nxt_simCode_idx != None:
                nxt_simCode_idx = gbl.execute_simCode_from_idx(nxt_simCode_idx)

            del  ev_list[0]
            main_ev_list.events_executed += 1


    def execute_all_lists(self, gbl, main_ev_list):
        ''' execute events in each list in turn'''
        gbl.set_current_sim_time(self.time)
        self.execute_list(gbl, main_ev_list, self.active_list)
        self.execute_list(gbl, main_ev_list, self.inactive_list)
        self.execute_list(gbl, main_ev_list, self.nonblocking_list)
        self.execute_list(gbl, main_ev_list, self.monitor_list)





class EventList(object):
    ''' The top level list of all events.
        It's just a time-ordered list of EventsAtOneTime objects.
    '''
    def __init__(self, end_time = 0xfffffffL ):

        self.events = []
        self.events_executed = 0

        # Add a terminating event at "infinity"
        self.events.append(EventsAtOneTime(end_time))

    def get_time_of_last_event(self):
        return self.events[-1].time


    def add_event(self, ev, c_time, list_type):
        ''' Add event to appropriate list within the current list of events.
            Assume there is one event list at max time.
        '''
        # Find the right EventsAtOneTime object to which we should add this event.
        # Create a new one if none exists at the desired time.
        for ix, ev_list in enumerate(self.events):
            if c_time == ev_list.time:
                return ev_list.add_event(ev, list_type)
            if c_time < ev_list.time: # need new EventsAtOneTime at this time.
                new_ev_list = EventsAtOneTime(c_time) 
                self.events.insert(ix, new_ev_list)
                return new_ev_list.add_event(ev, list_type)
        # asked to event after the end of simulation - so ignore it
        print "Warning: EventList.add_event: Asked to add event at time %d but that time is after end of simulation - event discarded." % c_time
        
    def __str__(self):
        s = ''
        for ev_list in self.events:
            s += '    t:%d  num_ev=%d\n' % (ev_list.time, ev_list.get_num_all_events() )
        return s


    def execute(self, gbl):
        ''' Run events until exhausted or forced to finish '''
        while (len(self.events)):
            evlist = self.events[0]
            
            evlist.execute_all_lists(gbl, self)

            del self.events[0]

        gbl.do_finish()
