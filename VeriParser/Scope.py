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
            
    def add_var(self, var):
        ''' Add variable to current scope '''
        if var.local_name in self.scopes[-1]:
            print "Error: variable name '%s' already used in current scope." % var.local_name
            return
        self.scopes[-1][var.local_name] = var

    def new_scope(self):
        self.scopes.append({})

    def del_scope(self):  
        ''' delete most recent scope '''
        assert len(self.scopes)>0
        del self.scopes[-1]


    def __str__(self):
        s = 'scopes='
        for scope in self.scopes:
            s += " [%s]" % ', '.join(scope.keys())
        return s