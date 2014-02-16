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

def get_range_min_max(a,b):
    if a<b: return (a,b) 
    return(b,a)


def process_reg_or_net_declaration(gbl, full_inst_name, parse_list):
    ''' create the regs or nets defined in the parse_list.
        e.g.   reg signed [31:0] r, s[2047:0]
        or     wire a,b,c;
        Actually create the specified VeriSignal objects
        and return them as a list of instances.
    '''
    regs      = []
    is_signed = False
    r_min     = r_max = 0   # range is 0 so far.

    for el in parse_list:

        obj_type = el[0]

        if obj_type == 'signed' : is_signed = True; continue

        if obj_type == 'range'  :
            r_min, r_max = get_range_min_max( int(el[1]), int(el[2]) )
            continue

        if obj_type == 'list_of_reg_identifiers' :
            for reg_id_list in el[1:]:
                reg_type = reg_id_list[0]
                if reg_type == 'reg_identifier':  # simple register definition.
                    reg_name = reg_id_list[1]
                    reg = VeriSignal.VeriSignal(mod_inst_name = full_inst_name,
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
                    reg = VeriSignal.VeriSignal(mod_inst_name = full_inst_name,
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
