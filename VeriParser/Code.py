##############################################
#
# Code.py
#
##############################################
''' Functions to return code snippets that would
then be exec'd to create Python functions.
'''
import Global, BitVector, EventList, sys

def code_get_signal_by_name(mod_inst, gbl, sig_name):
    ''' Return code that will can be eval's to return the veriSignal object
        associated with sign_name. sig_name could be local to the module or
        a global hierarchical name.
    '''
    if sig_name.find('.') >= 0:  # global name
        return "gbl.get_hier_signal('" + sig_name + "')"

    # local name. Must currently be in scope.
    sig = mod_inst.get_signal_from_name(sig_name)

    if not sig:
        print "Error: code_get_signal_by_name: could not find signal %s in module %s." % \
            (sig_name, mod_inst.full_inst_name)
        sys.exit(1)

    return "gbl.get_uniq_signal('%s')" % sig.uniq_name


def code_get_reg_or_number_temp_function(mod_inst, gbl, var_or_num):
    ''' var_or_num is either a reg_identifier or integer.
        temp function for simple expression.
    '''
    assert len(var_or_num) ==2
    if var_or_num[0] == 'reg_identifier' :
        return code_get_signal_by_name(mod_inst, gbl, var_or_num[1])+'.get_value()'
    else:
        return 'BitVector.BitVector(32, val_int=int(%s))' %  var_or_num[1]


def code_eval_expression(mod_inst, gbl, expr_list):
    print "\nexpr:", expr_list
    if expr_list[0] == '~':
        return code_eval_expression(mod_inst, gbl, expr_list[1:]) + \
            '.bitwise_negate()'
    if len(expr_list) == 1:
        return code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[0])
    assert len(expr_list) == 3  # x + y
    assert expr_list[1][0] == 'operator'
    assert expr_list[1][1] == '+'
    return '( %s + %s )' % (code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[0]), \
                            code_get_reg_or_number_temp_function(mod_inst, gbl, expr_list[2]) )


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



''' SimCode is actual Python code that can be executed at run time in the context
    of a Global object named gbl
'''
class SimCode(object):

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
