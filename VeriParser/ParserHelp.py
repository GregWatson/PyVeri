##################################################
#
# ParserHelp - helper functions
#
##################################################

import ParserError

simpleID_firstChar   = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
simpleID_restOfChars = simpleID_firstChar + '0123456789$'

def get_simple_identifier_at_offset( line, offset ):
    ''' Expect a simple identifier in line starting at offset.
        Return (err, name of identifier)
    '''
    l = len(line)
    if offset >= l: return (-1,'')
    if not line[offset] in simpleID_firstChar:  return (-1,'')
    end_pos = offset+1
    while end_pos < l:
        if not line[end_pos] in simpleID_restOfChars: return(0,line[offset:end_pos])
        end_pos += 1
    return(0,line[offset:end_pos])

##################################################
#
# balanced string functions.
#
# A balanced string is one that starts with an open pair 
# char such as ( or { or [ and which then ends with
# the apropriate closing pair char: )}]. But the functions
# allow the use of other pair chars inside, and only finish
# when the contents are balanced or there is no text left (err).
#
# 
##################################################

_opening_pair_chars = r'([{'
_closing_pair_chars = r')]}'
_closing_pair_char_of = { '(':')', '[':']', '{':'}' }

def get_comma_sep_exprs_from_balanced_string(line, nxt_pos, debug=0):
    ''' Given balanced string starting at line[nxt_pos], then try to parse
        line as a comma separated sequence of expressions. 
        First char of string must be an opening pair char.
        Return (err, list of exprs)
    '''
    l = len(line)
    if nxt_pos >= l: return ( ParserError.SE_SYNTAX_ERROR, [] )
    if line[nxt_pos] not in _opening_pair_chars: return ( ParserError.SE_SYNTAX_ERROR, [] )

    stack      = [ line[nxt_pos] ]
    pos        = nxt_pos+1
    expr_start = nxt_pos+1
    exprL      = []
    delim      = ','

    while pos < l :

        c = line[pos]

        if c in _closing_pair_chars:
            if c == _closing_pair_char_of[stack[-1]]:
                stack.pop()
                if debug: print "DBG: saw",c,"stack is now", stack
                if not stack: 
                    exprL.append( line[expr_start:pos].strip() )
                    return (0, exprL)
            else: # unbalanced pair - err
                if c == '(': return ( ParserError.SE_UNBALANCED_CLOSING_PAREN, [] )
                if c == '[': return ( ParserError.SE_UNBALANCED_CLOSING_BRKT , [] )
                if c == '{': return ( ParserError.SE_UNBALANCED_CLOSING_BRACE, [] )
                return( ParserError.SE_SYNTAX_ERROR, [] )
        else:
            if c in _opening_pair_chars:
                stack.append(c)
                if debug: print "DBG: saw",c,"stack is now", stack
            else:
                if c == delim:  # only have expr if stack len is 1. 
                    if len(stack) == 1:
                        exprL.append( line[expr_start:pos].strip() )
                        if debug: print "DBG: exprL is now", exprL
                        expr_start = pos+1

        pos += 1            

    return (ParserError.SE_NO_CLOSING_PAREN, [] )


####################################################
if __name__ == '__main__' :

    import unittest

    debug = 0

    class TestParserHelp(unittest.TestCase):
        def setUp(self): pass
        def tearDown(self):pass
        def checkList(self, L, expL):
            self.assert_(len(L) == len(expL), "exp return list:\n\t%s\nbut saw:\n\t%s" % (expL, L) )
            for ix in xrange(len(L)):
                self.assert_( L[ix] == expL[ix], "exp return list:\n\t%s\nbut saw:\n\t%s" % (expL, L) )
            
        def test1(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'(123 , "abc", f(1,2,"ab")[0:4] )', 0, debug )
            expL = [ '123', '"abc"', 'f(1,2,"ab")[0:4]' ]
            self.assert_(e==0, "Saw error %d" % e)
            self.checkList(L, expL)

    unittest.main()
