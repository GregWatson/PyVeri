##############################################
#
# Module class
#
##############################################

class VeriModule(object):

    module_names = []   # list of modules declared so far

    def __init__(self, d=None ): # d is parsed module structure from PyParsing
        self.name = 'no_name'
        self.port_list = []

    def get_range_min_max(self,a,b):
        if a<b: return (a,b) 
        return(b,a)

    def process_element(self, parse_list):
        ''' process a parsed object. First el is the name of the object type.
            Uses the dir(self) introspection to find functions named after 
            the type of the object in parse_list. It then invokes that function.
        '''
        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: unknown construct", parse_list[0]
            return
        getattr(self, obj_type_str)(parse_list[1:])


    def do_module_decl(self, parse_list):
        ''' top level module declaration parse object '''
        for el in parse_list:
            self.process_element(el)


    def do_module_name(self, parse_list): 
        ''' Set the module name '''
        mod_name = parse_list[0]
        if mod_name in VeriModule.module_names:
            print "Error: module name %s already defined." % mod_name
            return
        self.name = mod_name
        VeriModule.module_names.append(mod_name)


    def do_list_of_ports(self, parse_list):
        ''' simple list of port identifiers, not the port type declarations '''
        for port_id in parse_list:
            if port_id in self.port_list:
                print "Error: port '%s' used multiple times in port list for module %s" % \
                     (port_id, self.name)
            else:
                self.port_list.append(port_id)

    def do_module_item_list(self, parse_list):
        ''' pretty much anything in the body of a module... '''
        for el in parse_list: self.process_element(el)

    def create_simple_register(self, is_signed, r_min, r_max, reg_name):
        ''' Create a simple register of specified signed-edness and range. '''
        print "Info: module %s creating reg %s signed=%s [%d:%d]" %  \
                (self.name, reg_name, is_signed, r_max, r_min)

    def do_reg_declaration(self, parse_list):
        '''declare register or memory.
           reg signed [31:0] r, s[2047:0] '''
        is_signed = False
        r_min     = r_max = 0   # range is 0 so far.

        for el in parse_list:
            obj_type = el[0]
            if obj_type == 'signed' : is_signed = True; continue
            if obj_type == 'range'  :
                r_min, r_max = self.get_range_min_max( int(el[1]), int(el[2]) )
                continue
            if obj_type == 'list_of_reg_identifiers' :
                for reg_id_list in el[1:]:
                    reg_type = reg_id_list[0]
                    if reg_type == 'reg_identifier':  # simple register definition.
                        self.create_simple_register(is_signed, r_min, r_max, reg_id_list[1])
                continue
                
            print "Unknown reg_declaration object:", obj_type



    def to_string(self):
        s = 'name=%s' % self.name
        if self.port_list:
            s += "\nport_list=%s" % self.port_list
        return s


