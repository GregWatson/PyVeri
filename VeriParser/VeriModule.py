##############################################
#
# Module class
#
##############################################

import VeriSignal, Scope, EventList, Global
from Code import *
from CompilerHelp import *

class VeriModule(object):

    def __init__(self, timescale, hier='' ): 
        ''' timescale: timescale object created when module was defined (textually)
            hier: string. current hierarchy in which module is being instantiated
        '''
        self.full_inst_name = 'no_name' # full inst name. e.g. top.a1.b2.mod_inst_3
        self.name      = 'no_name'  # simple name (same for all instances of this module)
        self.hier      = hier
        self.port_list = []
        self.scope     = Scope.Scope() # new Scope object.
        self.timescale = timescale.copy() # timesale in place when this module was defined.


    def process_element(self, gbl, c_time, parse_list):
        ''' process a parsed object. First el is the name of the object type.
            Uses the dir(self) introspection to find functions named after 
            the type of the object in parse_list. It then invokes that function.
        '''
        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            print "Syntax error: process_element: unknown construct <", parse_list[0],">"
            print "(No method",obj_type_str,"). Parse list is:"
            print parse_list
            sys.exit(1)
        getattr(self, obj_type_str)(gbl, c_time, parse_list[1:])


    def do_always(self, gbl, c_time, parse_list):  # initial block
        print 'always:', parse_list

        # construct a function to be added at end of loop to jump back to start
        start_fn = SimCode( gbl )
        start_fn_idx =  start_fn.get_index()

        # fixme - might not be statement?
        assert parse_list[0] == 'statement'
        if parse_list[0] == 'statement':
            
            fn = self.process_statement_list( gbl, c_time,
                                              [parse_list],                  
                                              nxt_code_idx = start_fn.get_index() 
                                            )
            gbl.add_simcode_to_events(fn, c_time, 'active_list')

            # create the function that should be called at start of always loop.
            code =  '   ev = EventList.Event(simcode=gbl.get_simcode_by_idx(%d))\n' % fn.get_index()
            code += '   gbl.add_event(ev, gbl.time, "active_list")\n'
            code += '   return None'
            code_create_uniq_SimCode(gbl, code, code_idx = start_fn_idx)


    def do_initial(self, gbl, c_time, parse_list):  # initial block
        print 'initial:', parse_list
        assert parse_list[0] == 'statement'
        if parse_list[0] == 'statement':
            fn = self.process_statement_list( gbl, c_time, [parse_list]) # statement only has one el in list
            gbl.add_simcode_to_events(fn, c_time, 'active_list')

    def do_module_decl(self, gbl, c_time, parse_list):
        ''' top level module declaration parse object '''
        for el in parse_list:
            self.process_element(gbl, c_time, el)


    def do_module_name(self, gbl, c_time, parse_list): 
        ''' Set the module name '''
        mod_name = parse_list[0]
        self.name = mod_name
        self.full_inst_name = self.hier + mod_name
        gbl.add_mod_inst(self)

    def do_list_of_ports(self, gbl, c_time, parse_list):
        ''' simple list of port identifiers, not the port type declarations.
            e.g. module m(port1, port2, a, b, my_port).
            We simply add the port name to the list of names in
            self.port_list; we do not create signals at this point.
        '''
        for port_id in parse_list:
            if port_id in self.port_list:
                print "Error: port '%s' used multiple times in port list for module %s" % \
                     (port_id, self.name)
            else:
                self.port_list.append(port_id)

    def do_module_item_list(self, gbl, c_time, parse_list):
        ''' pretty much anything in the body of a module... '''
        for el in parse_list: self.process_element(gbl, c_time, el)


    def do_input_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more input wires within a module.
            e.g. input a,b,c;     or    input [31:0] z; 
            We check signal was declared as a port, create the signal,
            and make it a wire. May later get changed to a reg if it is
            explicitly declared to be such.
        '''
        print "do_input_declaration: ", 
        for el in parse_list: print el

        regs = process_input_or_output_declaration('in', gbl, self, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 


    def do_output_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more output wires within a module.
            e.g. output a,b,c;     or    output [31:0] z; 
            We check signal was declared as a port, create the signal,
            and make it a wire. May later get changed to a reg if it is
            explicitly declared to be such.
        '''
        print "do_output_declaration: ", 
        for el in parse_list: print el

        regs = process_input_or_output_declaration('out', gbl, self, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 


    def do_net_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more nets within a module.
            e.g. wire a,b,c; '''
        # NOTE: needs to be separate from do_reg_declaration cos wires 
        # doesnt support memories  (arrays)
        print "do_net_declaration: ", 
        for el in parse_list: print el

        regs = process_reg_or_net_declaration(gbl, self.full_inst_name, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 

        

    def do_reg_declaration(self, gbl, c_time, parse_list):
        '''declare register or memory.
           reg signed [31:0] r, s[2047:0] '''
        #fixme - memories not handled yet.
        print "do_reg_declaration: ", 
        for el in parse_list: print el

        regs = process_reg_or_net_declaration(gbl, self.full_inst_name, parse_list)

        for new_reg in regs:
            # Ports get auto-defined as nets (wires), so if they get declared
            # as regs then we need to redefine them.
            sig = self.scope.get_signal_from_name(new_reg.local_name) # None if not found
            if sig and sig.is_port:
                # Yes, it was already created as a port. Update it.
                if sig.port_dir == 'in':
                    self.error("defining port '%s' as register but it was already declared as an input." %
                                sig.local_name)
                print "converting wire",sig.local_name,"to reg."
                sig.sig_type = new_reg.sig_type
                sig.vec_min  = new_reg.vec_min
                sig.vec_max  = new_reg.vec_max
                sig.bit_vec  = new_reg.bit_vec

            else:
                gbl.add_signal( new_reg )
                self.scope.add_signal( new_reg ) 


    def do_continuous_assign(self, gbl, c_time, parse_list):
        ''' e.g. assign w = a + b, x = r; '''
        assert parse_list[0][0] == 'list_of_net_assignments'
        print "do_continuous_assign:"
        for ass in parse_list[0][1:]: 
            print "\t", ass
            assert ass[0] == 'net_assignment'
            assert len(ass) == 3 # 0='net_assignment', 1 = lvalue, 2=expr
            lvalue_list = ass[1]
            expr_list   = ass[2]

            # Because this is a wire assign we need to compute initial value and
            # assign it at time 0.
            lval_code       = code_get_signal_by_name(self, gbl, lvalue_list[1])
            expr_code, sigs = code_eval_expression(self, gbl, expr_list[1:])
            code            = '   ' + lval_code + '.set_value(' + expr_code + ')\n'
 
            # NOTE ----------------------------------------------------------
            # Probably want some general function that can handle expression
            # assignment to an lvalue. Keep the evaluation of expression separate
            # but then have a function that figures out the assignment to deal
            # with lvalue assigns such as:  { a[4:2], i, k[31:12] } = <expr>.
            # Would also be useful for module instantiation. 
            # ---------------------------------------------------------------

            simcode = gbl.create_and_add_code_to_events( code, c_time, 'active_list' )

            # Now we need to add the lvalue wire to the dependency list of all
            # signals in the expression (in sigs). In practice we need to recompute
            # the expression if any of the signals change. But we already have the
            # simcode to do that - we just need to invoke it when needed.


            print "[[[ Dep sigs: ",sigs,"]]]"
            if sigs: add_dependent_simcode_to_signals( simcode, sigs )


    def process_statement_list(self, gbl, c_time, parse_list, nxt_code_idx=None):
        ''' Process a list statement objects.
            parse_list: list of 'statement' objects. i.e. [ [ 'statement', [<parsed stmt info>]]  
                                                            [ 'statement', [<parsed stmt info>]] 
                                                            ...  
                                                          ]
            nxt_code_idx = index of simCode to be executed after the LAST one in
                           this block of statements (if any). 
                           The last simcode should return it.
            Return: simCode object for FIRST statement in parse_list
        '''
        print "process_statement_list: ["
        for el in parse_list: print "  <",el[0],":\n\t", el[1][0],"=", el[1][1:],">"
        print "]"
        first_stmt = parse_list[0]
        assert first_stmt[0] == 'statement'

        obj_type_str = 'do_st_' + first_stmt[1][0]  # e.g. do_st_seq_block
        if obj_type_str not in dir(self):
            print "Syntax error: process_statement_list: unknown construct", parse_list[0]
            print parse_list
            sys.exit(1)
        return getattr(self, obj_type_str)(gbl, c_time, first_stmt[1][1:], parse_list[1:], nxt_code_idx )


    def do_st_blocking_assignment(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' parse_list  = [ [lvalue]  [expr] ].
            return simCode for function for this stmt '''
        print "blocking_assignment: [",
        for el in parse_list: print "<",el,">",
        print "] (and %d items in stmt list)" % len(stmt_list)

        # Do this stmt
        assert len(parse_list) == 2  # fixme. we dont handle other stuff yet
        lvalue_list = parse_list[0]
        expr_list   = parse_list[1]

        lval_code       = code_get_signal_by_name(self, gbl, lvalue_list[1])
        expr_code, sigs = code_eval_expression(self, gbl, expr_list[1:])
        code            = '   ' + lval_code + '.set_value(' + expr_code + ')\n'
    
        # figure out where to go next (if anywhere)
        if len(stmt_list):
            next_fn = self.process_statement_list(gbl, c_time, stmt_list, nxt_code_idx)
            code   += '   return %d\n' % next_fn.get_index()
        else:
            code   += '   return %s\n' % str(nxt_code_idx)

        fn = code_create_uniq_SimCode( gbl, code)
        return fn


    def do_st_proc_timing_ctrl_stmt(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' parse_list is details of this statement. 
            Subsequent statements in stmt_list.
            Return first function for this statement.
        '''
        print "proc_timing_ctrl_stmt : delay= %s\n\t\tstmt=%s" % (parse_list[0], parse_list[1])

        timing_ctrl = parse_list[0]
        timing_stmt = parse_list[1]

        #process timing_stmt
        if len(stmt_list):
            next_fn        = self.process_statement_list(gbl, c_time, stmt_list,       nxt_code_idx)
            timing_stmt_fn = self.process_statement_list(gbl, c_time, [parse_list[1]], next_fn.get_index() )
        else:
            timing_stmt_fn = self.process_statement_list(gbl, c_time, [parse_list[1]], nxt_code_idx )


        # process timing ctrl

        if timing_ctrl[0] == 'delay_control': 
            delay_amount = compute_delay_time(self.timescale, timing_ctrl[1:])

            # create function that will add the timing_stmt later in time.
            code =  '   ev = EventList.Event(simcode=gbl.get_simcode_by_idx(%d))\n' % timing_stmt_fn.get_index()
            code += '   gbl.add_event(ev, gbl.time + %d, "active_list")\n' % delay_amount
            code += '   return None\n'
            timing_ctrl_fn = code_create_uniq_SimCode(gbl, code)

        return timing_ctrl_fn



    def do_st_seq_block(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' parse_list is list of lists '''
        print "seq_block: ["
        for el in parse_list: print "    <",el,">"
        print "] (and %d items in stmt list)" % len(stmt_list)

        self.scope.new_scope()

        # Remove any leading non-statements.
        while len(parse_list) and parse_list[0][0] != 'statement':
            print "do ",parse_list[0]   #fixme -- add code for this
            del parse_list[0] 

        # All remaining list elements SHOULD be statements. Execute them in order:
        # first stmt should return idx of second stmt, etc.
        if len(stmt_list):
            next_fn  = self.process_statement_list( gbl, c_time, stmt_list,  nxt_code_idx )
            first_fn = self.process_statement_list( gbl, c_time, parse_list, next_fn.get_index() )
        else:
            first_fn = self.process_statement_list( gbl, c_time, parse_list, nxt_code_idx)

        self.scope.del_scope()

        return first_fn


    def get_named_signal_from_scope(self, name):
        ''' Return VeriSignal object cor
responding to signal 'name'.
            name must be in this module.
            Return None if not found.
        '''
        return self.scope.get_signal_from_name(name)

    def error(self, *args):
        print "ERROR: In module '%s':" % self.name,
        for arg in args: print arg,
        print
        sys.exit(1)


    def __str__(self):
        s = 'Module %s (instance %s)' % (self.name, self.full_inst_name)
        if self.port_list:
            s += "\nport_list=%s" % self.port_list

        return s


