##############################################
#
# Code.py
#
##############################################
''' Functions to return code snippets that would
then be exec'd to create Python functions.
'''
import Global, BitVector, EventList, sys

def add_uniq(l1,l2):
    ''' add els in l2 to l1, but only if not in l1 already. '''
    l = l1[:]
    for el in l2:
        if el not in l: l.append(el)
    return l


def get_signal_by_name(mod_inst, gbl, sig_name):
    ''' Find and return the actual VeriSignal object corresponding to sig_name. 
        sig_name could be local to the module or a global hierarchical name.
    '''

    if sig_name.find('.') >= 0:  # global hier name
        sig = gbl.get_hier_signal(sig_name)

    else:
        # local name. Must currently be in scope.
        sig = mod_inst.get_named_signal_from_scope(sig_name)

    if not sig:
        print "Error: get_signal_by_name: could not find signal %s in module %s." % \
            (sig_name, mod_inst.full_inst_name)
        sys.exit(1)

    return sig


def code_get_signal_by_name(mod_inst, gbl, sig_name):
    ''' Return code that can be eval'd to return the veriSignal object
        associated with sign_name. sig_name could be local to the module or
        a global hierarchical name.
    '''
    sig = get_signal_by_name(mod_inst, gbl, sig_name)
    return "gbl.get_uniq_signal('%s')" % sig.uniq_name


def code_get_reg_or_number_temp_function(mod_inst, gbl, var_or_num):
    ''' var_or_num is either a reg_identifier or integer.
        temp function for simple expression.
        Return (code to evaluate var_or_num, list of sig if var_or_num is a signal )
    '''
    assert len(var_or_num) == 2
    if var_or_num[0] == 'reg_identifier' :

        code_to_get_sig = code_get_signal_by_name( mod_inst, gbl, var_or_num[1] )
        code = code_to_get_sig + '.get_value()'
        sig  = get_signal_by_name( mod_inst, gbl, var_or_num[1] )
        if not sig:
            print "code_get_reg_or_number_temp_function: cannot find signal object called %s.%s" % ( mod_inst.full_inst_name, var_or_num[1] )
            sys.exit(1)
        return (code, [sig])

    else:
        return ('BitVector.BitVector(32, val_int=int(%s))' %  var_or_num[1], [])


def code_eval_expression(mod_inst, gbl, expr_list, sigs=[] ):
    ''' Really dumb: either simple constant or "a+b". 
        Can be preceded by ~ (bitwise negate).
        Returns (code, [sigs] )
            where code is the text of the code to eval the expression.
            [sigs] is a list of signals (objects) used in the expression. (used for dependency checking)
    '''
    print "\nexpr:", expr_list

    if expr_list[0] == '~':
        code, new_sigs = code_eval_expression( mod_inst, gbl, expr_list[1:] )
        return (code + '.bitwise_negate()', add_uniq(sigs, new_sigs) )

    if len(expr_list) == 1:
        code, new_sigs = code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[0])
        return (code, add_uniq(sigs, new_sigs) )

    assert len(expr_list) == 3  # x + y
    assert expr_list[1][0] == 'operator'
    assert expr_list[1][1] == '+'
    code_x, sigs_x =  code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[0])
    code_y, sigs_y =  code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[2])
    code = code_x + ' + ' + code_y
    sigs = add_uniq(sigs, sigs_x)
    sigs = add_uniq(sigs, sigs_y)
    return ( code, sigs )


def code_create_uniq_SimCode(gbl, code, code_idx=None):
    ''' Create a SimCode object from code and return it.
    '''
    text = 'def f(gbl):\n' + code
    # print text
    try:
        exec text
    except Exception as e:
        print "Error: generated code for python function yielded exception:",e
        print "code was <\n",text,"\n>\n"
        sys.exit(1)
    return SimCode(gbl, idx=code_idx, fn=f, code_text=code)



''' SimCode is an object that has actual Python code that can be 
    executed at run time in the context of a Global object named gbl.
    The actual function should return the index of the NEXT SimCode
    to be executed in this sequence, else None.
'''
class SimCode(object):

    gbl = None  # gets set by gbl at runtime.

    def __init__( self, gbl, idx=None, fn=None, code_text=None ):
        self.fn = fn
        self.code_text = code_text
        if idx == None:
            self.fn_idx = gbl.get_new_simCode_idx()
        else:
            self.fn_idx = idx  # index of this function in the global list of simCodes.
        gbl.add_simCode(self)
        
    def get_index( self ):
        return self.fn_idx
