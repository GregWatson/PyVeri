##############################################
#
# Module class
#
##############################################

import VeriSignal, Scope, EventList
from Code import *

class VeriModule(object):

    def __init__(self, full_inst_name='' ): 
        self.name = 'no_name'  # name of the module (same for all instances of this module)
        self.full_inst_name = full_inst_name # full inst name. e.g. top.a1.b2.mod_inst_3
        self.port_list = []
        self.scope     = Scope.Scope() # new Scope object.


    def get_range_min_max(self,a,b):
        if a<b: return (a,b) 
        return(b,a)

    def process_element(self, gbl, c_time, parse_list):
        ''' process a parsed object. First el is the name of the object type.
            Uses the dir(self) introspection to find functions named after 
            the type of the object in parse_list. It then invokes that function.
        '''
        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: process_element: unknown construct", parse_list[0]
            print parse_list
            return
        getattr(self, obj_type_str)(gbl, c_time, parse_list[1:])

    def process_statement(self, gbl, c_time, parse_list):
        ''' Process a parser statement object. 
            Statements add events to the evnt list and return the new simulation time.
        '''
        print "process_statement: [",
        for el in parse_list: print "<",el,">",
        print "]"

        obj_type_str = 'do_st_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: process_statement: unknown construct", parse_list[0]
            print parse_list
            return
        return getattr(self, obj_type_str)(gbl, c_time, parse_list[1:])


    def do_st_blocking_assignment(self, gbl, c_time, parse_list):
        ''' parse_list  = [ [lvalue]  [expr] ].
            return code '''
        print "blocking_assignment: [",
        for el in parse_list: print "<",el,">",
        print "]"
        assert len(parse_list) == 2  # fixme. we dont handle other stuff yet
        lvalue_list = parse_list[0]
        expr_list   = parse_list[1]

        lval_code = code_get_signal_by_name(self, gbl, lvalue_list[1])
        expr_code = code_eval_expression(self, gbl, expr_list[1:])
        code      = lval_code + '.set_value(' + expr_code + ')'
        gbl.create_and_add_code_to_events( code, c_time, 'active_list')

        return c_time  # fixme


    def do_st_seq_block(self, gbl, c_time, parse_list): # begin ... end block. parse_list is a list of lists
        print "seq_block: ["
        for el in parse_list: print "    <",el,">"
        print "]"
        self.scope.new_scope()
        # process each statement in seq block
        self.scope.del_scope()
        return c_time


    def do_initial(self, gbl, c_time, parse_list):  # initial block
        print 'initial:'
        if parse_list[0] == 'statement':
            self.process_statement( gbl, c_time, parse_list[1]) # statement only has one el in list

    def do_module_decl(self, gbl, c_time, parse_list):
        ''' top level module declaration parse object '''
        for el in parse_list:
            self.process_element(gbl, c_time, el)


    def do_module_name(self, gbl, c_time, parse_list): 
        ''' Set the module name '''
        mod_name = parse_list[0]
        self.name = mod_name
        # if this is top level mdoule instance then full_inst_name is ''. 
        # In which case set it to be same as name.
        if not self.full_inst_name: self.full_inst_name = mod_name
        gbl.add_mod_inst(self)

    def do_list_of_ports(self, gbl, c_time, parse_list):
        ''' simple list of port identifiers, not the port type declarations '''
        for port_id in parse_list:
            if port_id in self.port_list:
                print "Error: port '%s' used multiple times in port list for module %s" % \
                     (port_id, self.name)
            else:
                self.port_list.append(port_id)

    def do_module_item_list(self, gbl, c_time, parse_list):
        ''' pretty much anything in the body of a module... '''
        for el in parse_list: self.process_element(gbl, c_time, el)


    def do_reg_declaration(self, gbl, c_time, parse_list):
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


    def get_signal_from_name(self, name):
        ''' Return VeriSignal object corresponding to signal 'name'
            Return None if not found.
        '''
        return self.scope.get_signal_from_name(name)


    def __str__(self):
        s = 'Module %s (instance %s)' % (self.name, self.full_inst_name)
        if self.port_list:
            s += "\nport_list=%s" % self.port_list

        return s


