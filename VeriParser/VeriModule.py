##############################################
#
## VeriModule class
#
##############################################

import VeriSignal, Scope, EventList, Global
from Code import *
from CompilerHelp import *

class VeriModule(object):

    ## Initialize routine for a new VeriModule object.
    # @param self : object
    # @param timescale : the timescale object created when module was defined (textually)
    # @param hier : string of the current hierarchy in which module is being instantiated.
    #               Use '' to indicate top-level module.
    # @return new VeriModule object
    def __init__(self, timescale, hier='' ): 

        self.full_inst_name = 'no_name' # full inst name. e.g. top.a1.b2.mod_inst_3
        self.name      = 'no_name'  # simple name (same for all instances of this module)
        self.hier      = hier
        self.port_list = []
        self.scope     = Scope.Scope() # new Scope object.
        self.timescale = timescale.copy() # timesale in place when this module was defined.


    ## Process one syntax object from the AST
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def process_element(self, gbl, c_time, parse_list):
        ''' Process a parse tree object created by the PyParsing parser.
            First element is the string name of the object type.
            Uses the dir(self) introspection to find the function named after 
            the type of the object in parse_list. 
            It then invokes that function on the remainder of the parse tree object.
        '''
        obj_type_str = 'do_' + parse_list[0]
        if obj_type_str not in dir(self):
            s = "Syntax error: process_element: unknown construct <%s>\n" %  parse_list[0]
            s += "(No method %s). Parse list is:\n" % obj_type_str
            s += str(parse_list)
            self.error(s)
        getattr(self, obj_type_str)(gbl, c_time, parse_list[1:])


    ## Process 'always' parser object.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_always(self, gbl, c_time, parse_list):  # initial block
        # print 'always:', parse_list

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


    ## Process 'initial' parser object.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_initial(self, gbl, c_time, parse_list):  # initial block
        # print 'initial:', parse_list
        assert parse_list[0] == 'statement'
        if parse_list[0] == 'statement':
            fn = self.process_statement_list( gbl, c_time, [parse_list]) # statement only has one el in list
            gbl.add_simcode_to_events(fn, c_time, 'active_list')



    ## Process 'module my_mod () ....  endmodule' declaration parser object.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_module_decl(self, gbl, c_time, parse_list):
        ''' top level module declaration parse object '''
        for el in parse_list:
            self.process_element(gbl, c_time, el)

    ## Process module name. e.g. 'my_mod' in 'module my_mod () ....  endmodule'
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_module_name(self, gbl, c_time, parse_list): 
        ''' In this case the modules' name and instance name are the same.
            hier is going to be '' so full_inst_name is just same as name.
        '''
        module_name = parse_list[0]
        self.set_instance_name( module_name, module_name)
        gbl.add_mod_inst(self)
        print "module",module_name,"created: full instance=",self.full_inst_name


    ## Process List of module ports.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_list_of_ports(self, gbl, c_time, parse_list):
        ''' Process the simple list of port identifiers, not the port type declarations.
            e.g. module m(port1, port2, a, b, my_port).
            We simply add the port name to the list of names in
            self.port_list; we do not create signals at this point.
        '''
        for port_id in parse_list:
            if port_id in self.port_list:
                self.error("Error: port '%s' used multiple times in port list for module %s" % \
                     (port_id, self.name) )
            else:
                self.port_list.append(port_id)

    ## Process Module instantiation. e.g. 'mod_name inst_name (.a(f), .b(g), ...);'
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_module_instantiation(self, gbl, c_time, parse_list):
        ''' Instantiate one or more modules by compiling the code for the module
            in the current context. Then we hook up the ports using assigns.
            Note: can be many instances of same module, such as:
            mod_name i1(.a(f), .b(g)), i2(.a(h), .b(j)), ... ;
            parse_list: [0] = module_identifier
                        [1] = optional parameter_value_assignment
                        [1..] = list of module_instance
        '''
        #print "do_module_instantiation", parse_list
        assert len(parse_list) > 1

        # fixme - might need to process optional parameter_value_assignment.
        
        module_name =  parse_list[0][1] # from  module_identifier     
        for module_instance in parse_list[1:] :
            self.instantiate_module(gbl, c_time, module_instance, module_name)
        

        sys.exit(1)


    ## Process module items. This means anything in the main body of a module declaration.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_module_item_list(self, gbl, c_time, parse_list):
        ''' pretty much anything in the body of a module... '''
        for el in parse_list: self.process_element(gbl, c_time, el)

    ## Process input declarations.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_input_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more input wires within a module.
            e.g. input a,b,c;     or    input [31:0] z; 
            We check signal was declared as a port, create the signal,
            and make it a wire. May later get changed to a reg if it is
            explicitly declared to be such.
        '''
        # print "do_input_declaration: ", 
        # for el in parse_list: print el

        regs = process_input_or_output_declaration('in', gbl, self, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 


    ## Process output declarations.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_output_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more output wires within a module.
            e.g. output a,b,c;     or    output [31:0] z; 
            We check signal was declared as a port, create the signal,
            and make it a wire. May later get changed to a reg if it is
            explicitly declared to be such.
        '''
        # print "do_output_declaration: ", 
        # for el in parse_list: print el

        regs = process_input_or_output_declaration('out', gbl, self, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 

    ## Process net (wire) declarations.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_net_declaration(self, gbl, c_time, parse_list):
        ''' Declare one or more nets within a module.
            e.g. wire a,b,c; 
                 wire [31:0] x,y;
        '''
        # NOTE: needs to be separate from do_reg_declaration cos wires 
        # doesnt support memories  (arrays)

        # print "do_net_declaration: ", 
        # for el in parse_list: print el

        regs = process_reg_or_net_declaration(gbl, self.full_inst_name, parse_list)

        for new_reg in regs:
            gbl.add_signal( new_reg )
            self.scope.add_signal( new_reg ) 

        
    ## Process reg declarations.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_reg_declaration(self, gbl, c_time, parse_list):
        '''Declare register or memory.
           e.g. reg signed [31:0] r, s[2047:0]
           If the reg corresponds to an output port then that port was already
           created as a wire, so we convert it to a register.
           NOTE: memories not handled yet!
        '''
        #fixme - memories not handled yet.

        # print "do_reg_declaration: ", 
        # for el in parse_list: print el

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
                # print "converting wire",sig.local_name,"to reg."
                sig.sig_type = new_reg.sig_type
                sig.vec_min  = new_reg.vec_min
                sig.vec_max  = new_reg.vec_max
                sig.bit_vec  = new_reg.bit_vec

            else:
                gbl.add_signal( new_reg )
                self.scope.add_signal( new_reg ) 


    ## Process continuous assign 
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @return None
    def do_continuous_assign(self, gbl, c_time, parse_list):
        ''' e.g. assign w = a + b, x = r; 
                 assign { a[31:0], {b,c[4]} } = z;
        '''
        assert parse_list[0][0] == 'list_of_net_assignments'
        for ass in parse_list[0][1:]: 
            assert ass[0] == 'net_assignment'
            assert len(ass) == 3 # 0='net_assignment', 1 = lvalue, 2=expr
            lvalue_list = ass[1]
            expr_list   = ass[2]

            # Because this is a wire assign we need to compute initial value and
            # assign it at time 0.
            expr_code, sigs = code_eval_expression(self, gbl, expr_list[1:])
            code            = code_assign_expr_code_to_lvalue(self, gbl, lvalue_list, expr_code)
 
            simcode = gbl.create_and_add_code_to_events( code, c_time, 'active_list' )

            # Now we need to add the lvalue wire to the dependency list of all
            # signals in the expression (in sigs). In practice we need to recompute
            # the expression if any of the signals change. But we already have the
            # simcode to do that - we just need to invoke it when needed.

            if sigs: add_dependent_simcode_to_signals( simcode, sigs )

    ## Process a list of statements.
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object from AST
    # @param nxt_code_idx : integer.
    # @return SimCode that will execute first part of first statement in list.
    def process_statement_list(self, gbl, c_time, parse_list, nxt_code_idx=None):
        ''' parse_list: list of 'statement' objects. i.e. [ [ 'statement', [<parsed stmt info>]]  
                                                            [ 'statement', [<parsed stmt info>]] 
                                                            ...  
                                                          ]
            nxt_code_idx = index of simCode to be executed after the LAST one in
                           this block of statements (if any). 
                           The last simcode created here should return it so that the
                           simulator knows which event (if any) to execute next.
            Return: simCode object for FIRST statement in parse_list.

            Uses introspection to find a function corresponding to the statement type.
            So if the ParseResult object has a first element string 'blocking_assignment'
            then this function will try to call a function do_st_blocking_assignment(...)
        '''

        #print "process_statement_list: ["
        #for el in parse_list: print "  <",el[0],":\n\t", el[1][0],"=", el[1][1:],">"
        #print "]"

        first_stmt = parse_list[0]
        assert first_stmt[0] == 'statement'

        obj_type_str = 'do_st_' + first_stmt[1][0]  # e.g. do_st_seq_block
        if obj_type_str not in dir(self):
            s = "Syntax error: process_statement_list: unknown construct %s.\n" % parse_list[0]
            s += str(parse_list)
            self.error(s)
        return getattr(self, obj_type_str)(gbl, c_time, first_stmt[1][1:], parse_list[1:], nxt_code_idx )

    ## Process a blocking assignment e.g. r1 = <expr>
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object for next statement to process.
    # @param stmt_list  : Subsequent statements in current list of statements (if any).
    # @param nxt_code_idx : integer.
    # @return SimCode that will execute first part of statement.
    def do_st_blocking_assignment(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' parse_list  = [ [lvalue]  [expr] ].
        '''
        # print "blocking_assignment: [",
        # for el in parse_list: print "<",el,">",
        # print "] (and %d items in stmt list)" % len(stmt_list)

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

    ## Process a timing control statement. e.g. #10 
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object for next statement to process.
    # @param stmt_list  : Subsequent statements in current list of statements (if any).
    # @param nxt_code_idx : integer.
    # @return SimCode that will execute first part of statement.
    def do_st_proc_timing_ctrl_stmt(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' process a statement such as
            #10 r=1;
            Here, '#10' is the timing ctrl and 'r=1' is the timing statement.
        '''
        # print "proc_timing_ctrl_stmt : delay= %s\n\t\tstmt=%s" % (parse_list[0], parse_list[1])

        timing_ctrl = parse_list[0]
        timing_stmt = parse_list[1]

        #process timing_stmt
        if len(stmt_list):
            next_fn        = self.process_statement_list(gbl, c_time, stmt_list,     nxt_code_idx)
            timing_stmt_fn = self.process_statement_list(gbl, c_time, [timing_stmt], next_fn.get_index() )
        else:
            timing_stmt_fn = self.process_statement_list(gbl, c_time, [timing_stmt], nxt_code_idx )


        # process timing ctrl

        if timing_ctrl[0] == 'delay_control': 
            delay_amount = compute_delay_time(self.timescale, timing_ctrl[1:])

            # create function that will add the timing_stmt later in time.
            code =  '   ev = EventList.Event(simcode=gbl.get_simcode_by_idx(%d))\n' % timing_stmt_fn.get_index()
            code += '   gbl.add_event(ev, gbl.time + %d, "active_list")\n' % delay_amount
            code += '   return None\n'
            timing_ctrl_fn = code_create_uniq_SimCode(gbl, code)

        return timing_ctrl_fn


    ## Process a sequential block statement. 
    # @param self : object
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : ParseResult object for sequential block statement.
    # @param stmt_list  : Subsequent statements in current list of statements (if any).
    # @param nxt_code_idx : integer.
    # @return SimCode that will execute first part of statement.
    def do_st_seq_block(self, gbl, c_time, parse_list, stmt_list, nxt_code_idx):
        ''' A sequential block is one or more statements between 'begin' and 'end'
        '''

        # print "seq_block: ["
        # for el in parse_list: print "    <",el,">"
        # print "] (and %d items in stmt list)" % len(stmt_list)

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

    ## Given local name (defined in module), return corresponding VeriSignal object.
    # @param self : object
    # @param name : string. 
    # @return VeriSignal object corresponding to name (from nearest scope).
    def get_named_signal_from_scope(self, name):
        ''' Return VeriSignal object corresponding to signal 'name'.
            name must be in this module.
            Return None if not found.
        '''
        return self.scope.get_signal_from_name(name)

    ## Given either local name (defined in module), or hierarchical name
    #  (e.g. top.m1.m2.my_signal) then return corresponding VeriSignal object.
    # @param self : object
    # @param gbl : Global object
    # @param name : string. 
    # @return VeriSignal object corresponding to name (from nearest scope) or None if not found.
    def get_signal_from_name(self, gbl, name):
        if name.find('.') != -1: # name contains a dot - hierarchical.
            return gbl.get_hier_signal(name)
        else:
            return self.get_named_signal_from_scope(name)



    ## Instantiate One module instance
    # @param self : parent VeriModule in which instance occurs.
    # @param gbl : The Global object
    # @param c_time : Integer. Current static time in the simulator (no longer needed?)
    # @param parse_list : module_instance ParseResult object for this one instance.
    # @param mod_name : String. Name of the module (not the instance name!)
    # @return None
    def instantiate_module( self, gbl, c_time, parse_list, mod_name ):
        assert len(parse_list)==3
        inst_name = parse_list[1][1]
        list_of_named_port_connections = parse_list[2][1:]
        print "instantiate_module: %s %s (%s)" % (mod_name, inst_name, list_of_named_port_connections)

        # Create the new module object and name it and register it with gbl.
        mod_inst = VeriModule( timescale = self.timescale, 
                               hier      = self.full_inst_name
                             )


        # Now we need to actually instantiate the mod_name module.
        # But we only know how to process a module declaration, so we copy
        # the Parse object for the base module declaration (for mod_name) and change the 
        # module name to be inst_name. Then we can just re-process the
        # module as though it were a declaration.
        # Then we need to connect the signals between the parent and the
        # instantiated module.

        parse_object = gbl.copy_parse_object_for_module(mod_name)

        # Let's just check this ...
        assert parse_object[0]    == 'module_decl'
        assert parse_object[1][0] == 'module_name'
        assert parse_object[1][1] == mod_name

        # change the name to be the full instance name
        parse_object[1][1] = inst_name

        # OK, now process the instance.
        mod_inst.process_element(gbl, 0, parse_object)

        # restore the module_name to be mod_name (rather than instance name)
        mod_inst.name = mod_name

        # Check port names used - must be present in the new instance.
        if not check_instance_port_names_against_module_port_names(
            self, 
            gbl, 
            list_of_named_port_connections,
            mod_inst
        ) : self.error("Port mismatch")

        # Connect top level signals to signals in the new instance.


    ## Set module name and full_inst_name.
    # @param self : object
    # @param name : string. Short module name
    # @return : None
    def set_instance_name(self, mod_name, inst_name):
        self.name = mod_name
        if len(self.hier):
            self.full_inst_name = self.hier + '.' + inst_name
        else:
            self.full_inst_name = inst_name
        print "Instantiated module",self.name,": full instance name =",self.full_inst_name


    ## Module error handling routine.
    # @param self : object
    # @param *args : list of strings to be printed in the error message.
    # @return : None  ( executes sys.exit(1) )
    def error(self, *args):
        print "ERROR: In module '%s':" % self.name,
        for arg in args: print arg,
        print
        sys.exit(1)


    ## Convert module to a printable string
    # @param self : object
    # @return : String
    def __str__(self):
        s = 'Module %s (instance %s)' % (self.name, self.full_inst_name)
        if self.port_list:
            s += "\nport_list=%s" % self.port_list

        return s


