##################################################
#
# CompilerHelp - helper functions
#
##################################################

import VeriSignal, Code, copy

def compute_delay_time( timescale, delay_stmt):

    # print "compute_delay_time:", delay_stmt
    time_in_fs = timescale.scale_number(float(delay_stmt[0]))
    # print "delay (fs) = ", time_in_fs
    return time_in_fs

def sort_as_min_max(a,b):
    if a<b: return (a,b) 
    return(b,a)

def sort_as_max_min(a,b):
    if a<b: return (b,a) 
    return(a,b)


## Parse a PyParsing _range object into two integers
# @param _range : PyParsing _range object
# @return (max, min) Integers
def parse__range_as_max_min_integers(_range):
    ''' _range is list e.g.: ['range', '7', '4'].
        Return tuple of ints: (max,min)  e.g. (7,4)
    '''
    assert len(_range) == 3, "Expected len 3 saw %d" % len(_range)
    return sort_as_max_min(int(_range[1]), int(_range[2]))


def get_just_signal_name(sig):
    ''' return just signal name. 
        e.g. if sig is 'count[12:11]' then return 'count'
    '''
    idx = sig.find('[')
    if idx != -1:
        return sig[0:idx]
    return sig
    
    

def process_reg_or_net_declaration(gbl, full_mod_inst_name, parse_list):
    ''' create the regs or nets defined in the parse_list.
        e.g.   reg signed [31:0] r, s[2047:0]
        or     wire a,b,c;
        Actually create the specified VeriSignal objects
        and return them as a list of instances.
        full_mod_inst_name : module name
    '''
    regs      = []
    is_signed = False
    r_min     = r_max = 0   # range is 0 so far.

    for el in parse_list:

        obj_type = el[0]

        if obj_type == 'signed' : is_signed = True; continue

        if obj_type == 'range'  :
            r_min, r_max = sort_as_min_max( int(el[1]), int(el[2]) )
            continue

        if obj_type == 'list_of_reg_identifiers' :
            for reg_id_list in el[1:]:
                reg_type = reg_id_list[0]
                if reg_type == 'reg_identifier':  # simple register definition.
                    reg_name = reg_id_list[1]
                    reg = VeriSignal.VeriSignal(mod_inst_name = full_mod_inst_name,
                                                sig_type      = 'reg',
                                                is_signed     = is_signed, 
                                                vec_min       = r_min, 
                                                vec_max       = r_max,
                                                local_name    = reg_name )
                    regs.append(reg)
                    continue
                else:
                    print "Internal Error: process_reg_or_net_declaration : unknown reg_type in list_of_reg_identifiers:", reg_type
                    return
            continue

        if obj_type == 'list_of_net_identifiers' :
            for reg_id_list in el[1:]:
                reg_type = reg_id_list[0]
                if reg_type == 'net_identifier':  # simple wire definition.
                    reg_name = reg_id_list[1]
                    reg = VeriSignal.VeriSignal(mod_inst_name = full_mod_inst_name,
                                                sig_type      = 'net',
                                                is_signed     = is_signed, 
                                                vec_min       = r_min, 
                                                vec_max       = r_max,
                                                local_name    = reg_name )
                    regs.append(reg)
                    continue
                else:
                    print "Internal Error: process_reg_or_net_declaration : unknown reg_type in list_of_net_identifiers:", reg_type
                    return
            continue

        print "Internal Error: process_reg_or_net_declaration : unknown parse tree object:", reg_type

    # print "process_reg_or_net_declaration: Returning",len(regs),"new registers/nets"
    return regs


def process_input_or_output_declaration(port_dir, gbl, module, parse_list):
    ''' process input a,b,c;   or   output [23:0] w,z;  etc.
        port_dir is 'in', 'out' or 'inout'

        Return list of signals created.
    '''
    regs = process_reg_or_net_declaration(gbl, module.full_inst_name, parse_list)

    for new_reg in regs:
        # should be in port_list
        if new_reg.local_name in module.port_list:
            new_reg.is_port  = True
            new_reg.port_dir = port_dir
        else:
            module.error(new_reg.local_name,"was not declared in module port list.")

    return regs
 

def add_dependent_simcode_to_signals( simcode, sigs ):
    ''' Given simcode (which assigns an expr to a signal)
        and a list of sigs, then add the simcode to the 
        list of dependent code for each signal in sigs.
        e.g. if code is "assign w = a+b" then the code 'w=a+b' 
             needs to be added as a dependent signal of a and b.
    '''
    for sig in sigs:
        sig.add_dependent_simcode(simcode)


## Connect instance port names to its parent module port names.
# @param parent_module : VeriModule within which the new instance is instantiated.
# @param gbl : Global object
# @param list_of_named_port_connections : ParseResult object of port connections.
# @param mod_inst : VeriModule object of the new instance.
# @return Boolean
def connect_instance_port_names_to_module_port_names(
        parent_module, gbl, list_of_named_port_connections, mod_inst 
    ) :
    for (port_i, expr) in list_of_named_port_connections:
        print port_i,"=>",expr

    for (port_i, expr) in list_of_named_port_connections:

        # first, check the named ports exist in the new instance.
        port_name = port_i[1]  # port_i[0] = 'port_identifier'

        sig = mod_inst.get_named_signal_from_scope(port_name)
        if not sig: return False

        # fixme - check port directions are compatible
        assert sig.is_port

        if sig.port_dir == 'in':  # create code for: assign port = <expr>
            print "Input Port is same as: assign %s = %s" % (sig.hier_name, str(expr[1:]) )

            expr_code, sigs = Code.code_eval_expression(parent_module, gbl, expr[1:])
            #print "expr_code=",expr_code,"   sigs in expr=",
            #for s in sigs: print s.hier_name,
            #print 

            # make the port name look like a net_identifier lvalue
            wire    = port_i[:]
            wire[0] = 'net_identifier'
            lvalue  = [ 'net_lvalue', wire ]
            
            # create code to assign the expr to the lvalue (port)
            code = Code.code_assign_expr_code_to_lvalue( mod_inst, gbl, lvalue, expr_code)

            print "Code=",code
            
            # Add event for initial assignment.
            simcode = gbl.create_and_add_code_to_events( code, 0, 'active_list' )

            # Now we need to add the lvalue to the dependency list of all
            # signals in the expression (in sigs). In practice we need to recompute
            # the expression if any of the signals change. But we already have the
            # simcode to do that - we just need to invoke it when needed.

            if sigs: add_dependent_simcode_to_signals( simcode, sigs )

        else: # sig port is output
            print "Output Port is same as:assign %s = %s" % (str(expr[1:]), sig.hier_name )

            # Create code to evaluate (look up) the value of the child module's signal.
            # First, make signal look like an expression.
            sig_expr = [ 'net_identifier', sig.local_name ]

            expr_code, sigs = Code.code_eval_expression(mod_inst, gbl, sig_expr)

            # Make the expr[1] look like an lvalue
            lvalue  = [ 'net_lvalue', expr[1:] ]
            
            print "lvalue is", str(lvalue), "\ncode to eval sig is",expr_code

            # create code to assign the expr to the lvalue (port)
            code = Code.code_assign_expr_code_to_lvalue( parent_module, gbl, lvalue, expr_code)

            print "Code=",code

            # Add event for initial assignment.
            simcode = gbl.create_and_add_code_to_events( code, 0, 'active_list' )

            # Now we need to invoke code whenever the child signal value changes.
            assert sigs # Must be exactly one.
            add_dependent_simcode_to_signals( simcode, sigs )
           
    return True

