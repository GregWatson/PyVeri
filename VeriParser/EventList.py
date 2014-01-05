##############################################
#
# Module EventList.py
#
##############################################

_next_uniq_fn = 0

def get_uniq_fn_name(base_name):
    ''' return a unique function name given a base name '''
    _next_uniq_fn += 1
    return "%s_%d" % (base_name, _next_uniq_fn)

class Event(object):
    ''' Single event in the event list '''
    
    def __init__(self):
        pass




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
