##################################################
#
# CompilerHelp - helper functions
#
##################################################

import VeriSignal

def compute_delay_time( timescale, delay_stmt):

    print "compute_delay_time:", delay_stmt
    time_in_fs = timescale.scale_number(float(delay_stmt[0]))
    print "delay (fs) = ", time_in_fs
    return time_in_fs

def sort_as_min_max(a,b):
    if a<b: return (a,b) 
    return(b,a)

def sort_as_max_min(a,b):
    if a<b: return (b,a) 
    return(a,b)

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
