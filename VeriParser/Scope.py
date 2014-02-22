##############################################
#
# Module Scope
#
# List of dictionaries. Each dict is a more recent scope (oldest at list[0] ):
# dict[ local_var_name ] = VeriSignal object
#
##############################################

class Scope(object):

    def __init__(self):
        self.scopes = [ {} ]

    def __getitem__(self, key):   # e.g. scope[key]
        if key > -1 and key < len(self.scopes):
            return self.scopes[key]
        else:
            print "Error: tried to access scope index %d but module only has %d scopes." \
                % (key,len(self.scopes))
            
    def add_signal(self, signal):
        ''' Add variable to current scope.
            signal: veriSignal 
        '''
        if signal.local_name in self.scopes[-1]:
            print "Error: signal name '%s' already used in current scope." % signal.local_name
            return
        self.scopes[-1][signal.local_name] = signal

    def new_scope(self):
        self.scopes.append({})

    def del_scope(self):  
        ''' delete most recent scope '''
        assert len(self.scopes)>0
        del self.scopes[-1]


    def is_top_of_module(self):
        ''' Return bool indicating if this is top level scope. '''
        return len(self.scopes) == 1

    def get_signal_from_name(self, name):
        ''' Return VeriSignal object corresponding to signal 'name'
            in the most recent scope (last-most)
            Return None if not found.
        '''
        for ix in range(len(self.scopes)-1, -1, -1):
            scope = self.scopes[ix]
            sig = scope.get(name, None)
            if sig: return sig
        return None


    def __str__(self):
        s = 'scopes='
        for scope in self.scopes:
            s += " [%s]" % ', '.join(scope.keys())
        return s
