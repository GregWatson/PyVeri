##############################################
#
# Code.py
#
##############################################
''' Functions to return code snippets that would
then be exec'd to create Python functions.
'''
import Global, BitVector, sys

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


def code_eval_expression(mod_inst, gbl, expr_list):
    return 'BitVector.BitVector(32, val_int=int(%s))' % expr_list[0] # fixme

def code_create_uniq_SimCode(gbl, code):
    ''' Create a SimCode object from code and return it.
    '''
    text = 'def f(gbl):' + code
    # print text
    try:
        exec text
    except Exception as e:
        print "Error: generated code for python function yielded exception:",e
        print "code was <",text,">"
        sys.exit(1)
    return SimCode(gbl, fn=f, code_text=code)



''' SimCode is actual paython code that can be executed at run time in the context
    of a Global object named gbl
'''
class SimCode(object):

    def __init__( self, gbl, fn=None, code_text=None ):
        self.fn = fn
        self.code_text = code_text
        gbl.add_simCode(self)
        
