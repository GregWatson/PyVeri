##############################################
#
# Module class
#
##############################################

class VeriModule(object):

    def __init__(self, d=None ): # d is parsed module structure from PyParsing
        self.name = 'no_name'
        self.port_list = []


    def to_string(self):
        s = 'name=%s' % self.name
        if self.port_list:
            s += "\nport_list=%s" % self.port_list
        return s
