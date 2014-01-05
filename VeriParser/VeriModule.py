##############################################
#
# Module class
#
##############################################

import VeriSignal, Scope, EventList

class VeriModule(object):

    def __init__(self, full_inst_name='' ): 
        self.name = 'no_name'  # name of the module (same for all instances of this module)
        self.full_inst_name = full_inst_name # full inst name. e.g. top.a1.b2.mod_inst_3
        self.port_list = []
        self.scope     = Scope.Scope() # new Scope object.


    def get_range_min_max(self,a,b):
        if a<b: return (a,b) 
        return(b,a)

    def process_element(self, gbl, parse_list):
        ''' process a parsed object. First el is the name of the object type.
            Uses the dir(self) introspection to find functions named after 
            the type of the object in parse_list. It then invokes that function.
        '''
        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: process_element: unknown construct", parse_list[0]
            print parse_list
            return
        getattr(self, obj_type_str)(gbl, parse_list[1:])

    def process_statement(self, gbl, parse_list):
        ''' Process a parser statement object. Need to return an
            event object that can be added to an event queue.
        '''
        print "process_statement: [",
        for el in parse_list: print "<",el,">",
        print "]"

        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: process_statement: unknown construct", parse_list[0]
            print parse_list
            return
        return getattr(self, obj_type_str)(gbl ,parse_list[1:])


    def do_blocking_assignment(self, gbl, parse_list):
        ''' parse_list  = [ [lvalue]  [expr] ].
            return code '''
        print "blocking_assignment: [",
        for el in parse_list: print "<",el,">",
        print "]" 
        lvalue_list = parse_list[0]
        self.scope.check_var_in_scope(lvalue_list[1])
        return 0  # fixme


    def do_seq_block(self, gbl, parse_list): # begin ... end block. parse_list is a list of lists
        print "seq_block: ["
        for el in parse_list: print "    <",el,">"
        print "]"
        self.scope.new_scope()
        # process each statement in seq block
        self.scope.del_scope()
        return 0  # fixme


    def do_initial(self, gbl, parse_list):  # initial block
        print 'initial:'
        if parse_list[0] == 'statement':
            s = self.process_statement( gbl, parse_list[1]) # statement only has one el in list
        print "[[[ do_initial: Need to add statement to event list at time 0 ]]]"

    def do_module_decl(self, gbl, parse_list):
        ''' top level module declaration parse object '''
        for el in parse_list:
            self.process_element(gbl, el)


    def do_module_name(self, gbl, parse_list): 
        ''' Set the module name '''
        mod_name = parse_list[0]
        self.name = mod_name
        # if this is top level mdoule instance then full_inst_name is ''. 
        # In which case set it to be same as name.
        if not self.full_inst_name: self.full_inst_name = mod_name
        gbl.add_mod_inst(self)

    def do_list_of_ports(self, gbl, parse_list):
        ''' simple list of port identifiers, not the port type declarations '''
        for port_id in parse_list:
            if port_id in self.port_list:
                print "Error: port '%s' used multiple times in port list for module %s" % \
                     (port_id, self.name)
            else:
                self.port_list.append(port_id)

    def do_module_item_list(self, gbl, parse_list):
        ''' pretty much anything in the body of a module... '''
        for el in parse_list: self.process_element(gbl, el)


    def do_reg_declaration(self, gbl, parse_list):
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
                        reg_name = reg_id_list[1]
                        reg = VeriSignal.VeriSignal(mod_inst_name = self.full_inst_name,
                                                    is_signed     = is_signed, 
                                                    vec_min       = r_min, 
                                                    vec_max       = r_max,
                                                    local_name    = reg_name )
                        gbl.add_signal( reg )
                        self.scope.add_signal( reg ) 
                        print self.scope
                        continue
                    else:
                        print "Internal Error: Unknown list_of_reg_identifiers object:", reg_type
                        return
                return

            print "Internal Error: Unknown reg_declaration object:", obj_type


    def __str__(self):
        s = 'Module %s (instance %s)' % (self.name, self.full_inst_name)
        if self.port_list:
            s += "\nport_list=%s" % self.port_list

        return s


