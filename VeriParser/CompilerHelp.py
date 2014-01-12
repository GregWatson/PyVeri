##################################################
#
# CompilerHelp - helper functions
#
##################################################


def compute_delay_time( timescale, delay_stmt):

    print "compute_delay_time:", delay_stmt
    time_in_fs = timescale.scale_number(float(delay_stmt[0]))
    print "delay (fs) = ", time_in_fs
    return time_in_fs
