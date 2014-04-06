##############################################
#
# Code.py
#
##############################################
''' Functions to return code snippets that would
then be exec'd to create Python functions.
'''
import Global, BitVector, EventList, VeriExceptions
import sys
from CompilerHelp import *

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

## Check that the number of bits is enough to hold the specified value.
# @param i_width : Integer. number of bits specified.
# @param i_val   : Integer. integer value.
# @return Boolean or else report error
def check_width_big_enough_for_value(i_width, i_val, i_is_x, expr):
    bits_needed = 0
    while i_val or i_is_x:
        bits_needed += 1
        i_val >>= 1 ; i_is_x >>= 1
    if bits_needed == 0: bits_needed = 1
    if bits_needed > i_width:
        print "Error: expression has too few bits to represent value. Specified",i_width,"but need",bits_needed
        print "       expression:",expr
        raise VeriExceptions.InsufficientWidthError,''
    return True
    


## Return width(bits), decimal value and is_x data for an integer expression. If no explicit width then it's 32.
# @param expr : PyParsing object e.g.  ['number', ['unsigned_integer', '32', '2147483648','0']]
# @return (width, value, is_x) as integers.
def get_width_value_is_x_of_number(expr):
    assert expr[0] == 'number'
    i_val = None
    num = expr[1]
    i_is_x = 0
    if num[0] == 'unsigned_integer':
        assert len(num)==4  # str, width, i_val, is_x 
        i_width = int(num[1])
        i_val   = int(num[2])
        i_is_x  = int(num[3]) 

        if i_val != None:
            check_width_big_enough_for_value(i_width, i_val, i_is_x, num)
            return (i_width, i_val, i_is_x)

    print "Error: get_width_and_value_of_number: unknown number expression:",expr_list
    sys.exit(1)    



## Evaluate a compile-time constant expression, returning the value.
# @param expr : PyParsing object e.g.  ['number', ['unsigned_integer', '32', '2147483648']]
# @return compile-time value of the expression such as integer or string
def eval_const_expression(expr):
    ''' expression can contain variables that are evaluated at compile time.
        e.g. int i; for (i=0;i<5;i=i+1) begin r[i] = 0; end
    '''
    # fixme - only dealing with simple integers at the moment.
    print "eval_const_expression: expr is:",expr
    assert len(expr)>=2,"expr is %s" % expr
    assert expr[0] == 'number'
    i_width, i_val, i_is_x = get_width_value_is_x_of_number(expr)
    return i_val
    print "Error: code_eval_expression_as_integer: unknown number expression:",expr_list
    sys.exit(1)


def code_get_signal_by_name(mod_inst, gbl, sig_name):
    ''' Return code that can be eval'd to return the veriSignal object
        associated with sign_name. sig_name could be local to the module or
        a global hierarchical name.
    '''
    sig = get_signal_by_name(mod_inst, gbl, sig_name)
    return "gbl.get_uniq_signal('%s')" % sig.uniq_name

## Evaluate a number object. Return code that will create the equivalent BitVector object
# @param expr : PyParsing number object.
# @return code - String for code to create the bitvector.
def code_eval_number( expr ):
    ''' examples of expr (number):
        ['number', ['unsigned_integer', '8', '2147483648']]
    '''
    print "code_eval_number", expr
    assert len(expr) >1
    assert expr[0] == 'number'

    typ = expr[1][0]

    if typ == 'unsigned_integer': # integer, optional length
        i_width, i_val, i_is_x = get_width_value_is_x_of_number(expr)
        return('BitVector.BitVector(num_bits=%s, val_int=int(%s), is_x=(%s))' %  (i_width, i_val, i_is_x))

    else:
        print "Error: code_eval_number: unknown number type", typ
        sys.exit(1)



def code_eval_expression_as_integer(mod_inst, gbl, expr_list, sigs=[] ):
    ''' Only simple expressions.
        Evaluate an expression but return it as an integer (not as BitVector)
        expr_list: expression list without leading 'expression' string.
                   e.g. ['number', ['unsigned_integer', '32', '2147483648']]  or
                        ['~', ['net_identifier', 'r']]  or
                        [ ['net_identifier', 'a'], '+', 
                          [['net_identifier', 'b'], '*', ['net_identifier', 'c']]
                        ]


        sigs: initial list of signals (not constants) used in 
              any surrounding expression.
        Returns (code, [sigs] )
            code: the text of the code to eval the expression.
                  This code will return an integer.
            [sigs]: a list of any signals (verisignal objects, not constants) 
                    used in the expression. 
                    (it is used for determining signal dependency)
    '''
    
    print "\nexpr:len=", len(expr_list)," expr=",expr_list
    
    #optimize if it's a constant
    if len(expr_list)>1:
        if expr_list[0] == 'number':
            i_width, i_val, i_is_x = get_width_value_is_x_of_number(expr_list)
            return ( str(i_val), sigs)

    code, new_sigs = code_eval_expression(mod_inst, gbl, expr_list, sigs) 
    code += '.to_integer()'
    return (code, new_sigs)



def code_eval_expression(mod_inst, gbl, expr_list, sigs=[] ):
    ''' Only simple expressions.
        Can be preceded by ~ (bitwise negate).
        expr_list: expression list without leading 'expression' string.
                   e.g. ['uint', 1] or 
                        ['~', ['net_identifier', 'r']]  or
                        [ ['net_identifier', 'a'], '+', 
                          [['net_identifier', 'b'], '*', ['net_identifier', 'c']]
                        ]


        sigs: initial list of signals (not constants) used in 
              any surrounding expression.
        Returns (code, [sigs] )
            code: the text of the code to eval the expression.
                  This code will return a BitVector object. 
                  (should return a copy if the bitvec already exists in a signal)
            [sigs]: a list of any signals (verisignal objects, not constants) 
                    used in the expression. 
                    (it is used for determining signal dependency)
    '''
    print "\nexpr:len=", len(expr_list)," expr=",expr_list
    
    if len(expr_list) == 2:
        typ = expr_list[0]  # could be literal or object type.
        val = expr_list[1]

        if typ == '~': # bit invert
            code, new_sigs = code_eval_expression( mod_inst, gbl, val )
            return (code + '.bitwise_negate()', add_uniq(sigs, new_sigs) )

        if typ == 'number': 
            return ( code_eval_number(expr_list), sigs)

        if typ == 'net_identifier': 
            code = code_get_signal_by_name( mod_inst, gbl, val ) + '.get_value()'
            sig  = get_signal_by_name( mod_inst, gbl, val )
            if not sig:
                print "code_eval_expression: cannot find signal object called %s.%s" % ( 
                            mod_inst.full_inst_name, val )
                sys.exit(1)
            return (code,  add_uniq(sigs, [sig]))


        print "code_eval_expression: Error: unknown expr type: '%s'" % typ
        print "                      Expr was:", expr_list
        sys.exit(1)            

    if len(expr_list) == 3:

        if isinstance(expr_list[0], basestring):

            typ  = expr_list[0]  # string
            val1 = expr_list[1]
            val2 = expr_list[2]
            print "typ=",typ," val1=",val1," val2=",val2

            if typ == 'net_identifier_expr': # e.g. r[3+2] or r1[31]

                assert val1[0] == 'net_identifier'
                assert val2[0] == 'expression'

                code_to_get_sig = code_get_signal_by_name( mod_inst, gbl, val1[1] )
                sigs1 = [ get_signal_by_name( mod_inst, gbl, val1[1] ) ] 
                if not sigs1:
                    print "code_eval_expression: cannot find signal object called %s.%s" % ( 
                                mod_inst.full_inst_name, val1[1] )
                    sys.exit(1)
                sigs = add_uniq(sigs, sigs1)

                code_to_eval_bit_sel, sigs = code_eval_expression_as_integer(mod_inst, gbl, val2[1:], sigs)
                code = code_to_get_sig + '.get_value(self_max=%s)' % code_to_eval_bit_sel

                print "code=",code
                if len(sigs): 
                    print "sigs:", 
                    for s in sigs: print "\t",s.hier_name
                return (code, sigs)

            if typ == 'net_identifier_range': # e.g. r[3:0] 

                assert val1[0] == 'net_identifier'
                assert val2[0] == 'range'  # PyParsing _range object

                code_to_get_sig = code_get_signal_by_name( mod_inst, gbl, val1[1] )
                sigs1 = [ get_signal_by_name( mod_inst, gbl, val1[1] ) ] 
                if not sigs1:
                    print "code_eval_expression: cannot find signal object called %s.%s" % ( 
                                mod_inst.full_inst_name, val1[1] )
                    sys.exit(1)
                sigs = add_uniq(sigs, sigs1)

                range_max, range_min = parse__range_as_max_min_integers(val2)
                code = code_to_get_sig + '.get_value(self_max=%d, self_min=%d)' % \
                                            (range_max, range_min)

                print "code=",code
                if len(sigs): 
                    print "sigs:", 
                    for s in sigs: print "\t",s.hier_name
                return (code, sigs)

        else:
            if isinstance(expr_list[1], basestring):

                op1    = expr_list[0]  
                opcode = expr_list[1] # e.g. +,- etc
                op2    = expr_list[2]

                code1, sigs = code_eval_expression(mod_inst, gbl, op1, sigs )
                code2, sigs = code_eval_expression(mod_inst, gbl, op2, sigs )
                code = "(%s %s %s)" % (code1, opcode, code2)

                print "op1 opcode op2 code=",code
                if len(sigs): 
                    print "sigs:", 
                    for s in sigs: print "\t",s.hier_name

                return (code, sigs)


        print "code_eval_expression: Error: unknown expr type: '%s'" % typ
        print "                      Expr was:", expr_list
        sys.exit(1)            


    print "code_eval_expression: Error: unexpected expr length:", len(expr_list)
    print "                      Expr was:", expr_list
    sys.exit(1)            


## Compare two expressions and execute either true code or false code
# @param lval_code : string. Code to evaluate left  hand of comparison
# @param rval_code : string. Code to evaluate right hand of comparison
# @param if_true_code  : string. Code to be executed if comparison is true.
# @param if_false_code : string. Code to be executed if comparison is false.
# @return code - String
def code_compare_values(lval_code, rval_code, if_true_code, if_false_code):
    ''' produce code for:
        if (lval_code) == (rval_code):
            if_true_code
        else:
            if_false_code
    '''
    code =  'if ( (%s) == (%s) ) :\n' % (lval_code, rval_code)
    code += '   ' + if_true_code + '\n'
    code += 'else:\n'
    code += '   ' + if_false_code + '\n'
    return code




def flatten_net_concat_into_name_max_min(mod_inst, gbl, lvalue):
    ''' Given an lvalue, remove the hierarchy and return a list
        of tuples of form (verisignal, max_index, min_index)
        where max_index and min_index are the bit range specified
        in the lvalue. 
        e.g. lvalue was from src text: {w1,w2[3:0],{a,b}} 
            then return something like [ (<w1>,31,0), (<w2>,3,0), (<a>,0,0), (<b>,7,0) ]
        lvalue: pyparsing net_lvalue object
    '''
    print "lvalue=", lvalue
    assert lvalue[0].endswith('_lvalue'),"SAW: %s " % lvalue
    lvalue_type = lvalue[1][0]

    if lvalue_type == 'net_identifier':
        # look up defined signal to find width. 
        sig = mod_inst.get_signal_from_name(gbl, lvalue[1][1])
        return [ (sig, sig.vec_max, sig.vec_min) ]

    if lvalue_type == 'net_identifier_range':
        sig = mod_inst.get_signal_from_name(gbl, lvalue[1][1][1])
        lmax, lmin = parse__range_as_max_min_integers(lvalue[1][2])
        return [ (sig, lmax, lmin) ]

    if lvalue_type == 'net_identifier_expr': # e.g. f[2+3]
        sig = mod_inst.get_signal_from_name(gbl, lvalue[1][1][1])
        assert lvalue[1][2][0] == 'expression'  
        const_expr = lvalue[1][2][1:]
        bit_sel_val = eval_const_expression(const_expr)

        return [ (sig, bit_sel_val, bit_sel_val) ]

    if lvalue_type == 'net_concatenation':
        l = []
        for concat_lvalue in lvalue[1][1:] :
            l.extend( flatten_net_concat_into_name_max_min(mod_inst, gbl, concat_lvalue) )
        return l

    # fixme - code net_identifier_expr

    assert False, "flatten_net_concat_into_name_max_min: type %s not coded." % lvalue_type



def count_signals_in_lvalue(lvalue):
    ''' Return the number of signals in an lvalue object.
        e.g. if lvalue is just wire w then number of signals is 1.
             if lvalue is  { a, b[20:8], z, { c[3],c[6] } }  then number of signals is 5.
        lvalue: pyparsing lvalue object
        Return: integer number of signals
    '''
    assert lvalue[0].endswith('_lvalue'),"SAW: %s " % lvalue
    # unless the lvalue type is concatenation then len is 1.
    if lvalue[1][0] == 'net_concatenation':
        return sum( map (count_signals_in_lvalue, lvalue[1][1:] ) )
    else:
        return 1

def code_assign_expr_bits_to_simple_lvalue(mod_inst, gbl, lvalue, expr_code):
    ''' given a simple lvalue (e.g. w or w[2+4] or w[4:3] but NOT a concatenation!)
        then return code that assigns expr_code to it.
    '''
    print "code_assign_expr_bits_to_simple_lvalue: lvalue=",lvalue

    net_type = lvalue[1][0]

    if net_type.endswith('_identifier'):

        lval_code  = code_get_signal_by_name(mod_inst, gbl, lvalue[1][1])
        code       = lval_code + '.set_value(' + expr_code + ')\n'

    elif net_type.endswith('_identifier_range'):

        lval_code  = code_get_signal_by_name(mod_inst, gbl, lvalue[1][1][1])
        lmax, lmin = parse__range_as_max_min_integers(lvalue[1][2])
        bit_sel_str = ',self_max = %d, self_min = %d' % (lmax, lmin)
        code       = lval_code + '.set_value(' + expr_code + bit_sel_str + ')\n'
        
    elif net_type.endswith('_identifier_expr'): # e.g. r[2+3]

        net_name  = lvalue[1][1][1]
        lval_code = code_get_signal_by_name(mod_inst, gbl, net_name)

        bit_sel_expr      = lvalue[1][2][1:] # e.g. ['uint', '7']
        bit_sel_code,sigs = code_eval_expression(mod_inst, gbl, bit_sel_expr )

        #print "target is",net_name,bit_sel_expr
        #print "code to eval bit select expr is:", bit_sel_code
        # We need to use the bit_sel_code for min and max bit position, so assign to tmp.
        code        = 'bit_min_max = ' + bit_sel_code + ".get_bin_data()\n"
        bit_sel_str = ',self_max = bit_min_max, self_min = bit_min_max'
        code       += lval_code + '.set_value(' + expr_code + bit_sel_str + ')\n'
        # print "final code is\n",code    

    else: 
        assert False,"\ncode_assign_expr_bits_to_simple_lvalue:Unknown net_type:" + net_type

    return code

def code_assign_expr_code_to_lvalue(mod_inst, gbl, lvalue, expr_code):
    ''' given the code to compute an expression, now construct the code
        to assign it to the lvalue (parse object).
        mod_inst: module where we are making assignment
        lvalue: pyparsing object for an lvalue
        expr_code: string of code that evaluates the expression
        Returns: string of code that assigns expr to lvalue.
    '''
    #print "code_assign_expr_code_to_lvalue: assign\n   ",expr_code,"\nto\n   ", lvalue
    # fixme - need to handle different lvalue types.
    num_lvalue_sigs = count_signals_in_lvalue(lvalue)
    # print "code_assign_expr_code_to_lvalue: saw ", lvalue


    # If we only have one lvalue then we can just assign expression to it.
    # e.g. w = <expr>
    # But if we have several then we need to assign the expression to a variable
    # so that we can reference it for each lvalue signal.
    # e.g. src is    { a,b } = <expr>
    if num_lvalue_sigs == 1:
        code = code_assign_expr_bits_to_simple_lvalue(mod_inst, gbl, lvalue, expr_code)

    else:  # {a,b[3:0] ,...} = expr
        
        # Need to keep expr around - assign it to a var
        code = "tmp_bv = " + expr_code + "\n"

        lval_list = flatten_net_concat_into_name_max_min(mod_inst, gbl, lvalue) # left to right order
        expr_min = 0  
        # need to process list right to left
        for (sig,max_bit,min_bit) in lval_list[-1::-1]:

            expr_max = expr_min + max_bit - min_bit

            # foreach we need code such as : lvalue[max:min] = tmp_bv[max:min]
            code += code_get_signal_by_name( mod_inst, gbl, sig.local_name)
            code += '.set_value(tmp_bv, self_max=%d, self_min=%d, bv_max=%d, bv_min=%d)\n' % (
                    max_bit, min_bit, expr_max, expr_min)

            expr_min = expr_max + 1  # start next assign at next m.s.bit

    return code


def code_create_uniq_SimCode(gbl, code, code_idx=None):
    ''' Create a SimCode object from code and return it.
    '''
    new_code = code.split('\n')
    new_code = [ '    ' + c for c in new_code ]
    new_code = '\n'.join(new_code)

    text = 'def f(gbl):\n' + new_code
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

    def __str__(self):
        return "[idx=%d  code=%s]" % (self.fn_idx, self.code_text)
