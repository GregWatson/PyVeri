##############################################
#
# Module EventList.py
#
##############################################

_next_uniq_fn = 0

def get_uniq_fn_name(base_name):
    ''' return a unique function name given a base name '''
    _next_uniq_fn += 1
    return "%s_%d" % (base_name, _next_uniq_fn)

