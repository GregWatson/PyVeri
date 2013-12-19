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


def find_first_simple_id_substr(text, sub, offset):
    ''' Find earliest occurrence of simple_ID sub in text starting from start.
        The simple_ID must be a complete word - not a substring.
        So looking for sub x in 'xx x' should return 3 not 0.
        return position where sub starts, else -1
    '''
    if not len(text) or not len(sub): return -1
    start = offset
    while start < len(text):
        pos = text.find(sub, start)
        if pos == -1: return -1
        start = pos + 1  # ready to keep looking if pos doesnt work out.

        # if previous char is legal in simple_ID then this is not a match
        if pos > 0 and ( text[pos-1] in simpleID_restOfChars ) : continue

        # if char after sub is legal in simple_ID then this is not a match
        nxt = pos + len(sub)
        if nxt < len(text) and ( text[nxt] in simpleID_restOfChars ) : continue

        return pos

    return -1

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
    if nxt_pos >= l: 
        print "Internal ERROR:get_comma_sep_exprs_from_balanced_string: next_pos arg outside string."
        return ( ParserError.SE_SYNTAX_ERROR, [] )
    if line[nxt_pos] not in _opening_pair_chars: 
        print "Internal ERROR:get_comma_sep_exprs_from_balanced_string: start char is not in", _opening_pair_chars
        return ( ParserError.SE_SYNTAX_ERROR, [] )

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
                if c == ')': return ( ParserError.SE_UNBALANCED_CLOSING_PAREN, [] )
                if c == ']': return ( ParserError.SE_UNBALANCED_CLOSING_BRKT , [] )
                if c == '}': return ( ParserError.SE_UNBALANCED_CLOSING_BRACE, [] )
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

        #############################################
        # test  get_comma_sep_exprs_from_balanced_string()
        #############################################

        def test1(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'(123 , ["ab{}c"], f(1,2,"ab")[0:4], )', 0, debug )
            expL = [ '123', '["ab{}c"]', 'f(1,2,"ab")[0:4]','' ]
            self.assert_(e==0, "Saw error %d" % e)
            self.checkList(L, expL)

        def test2(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'(,  )', 0, debug )
            expL = [ '', '' ]
            self.assert_(e==0, "Saw error %d" % e)
            self.checkList(L, expL)

        def test3(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 11, debug )
            expL = [ 'abc{,}', '123' ]
            self.assert_(e==0, "Saw error %d" % e)
            self.checkList(L, expL)

        def test4(self):
            print "\nExpect Internal ERROR:"
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 99, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_SYNTAX_ERROR and not len(L), "Saw error %d" % e)

        def test5(self):
            print "\nExpect Internal ERROR:"
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 2, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_SYNTAX_ERROR and not len(L), "Saw error %d" % e)

        def test6(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'[)', 0, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_PAREN and not len(L), "Saw error %d" % e)
        def test7(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'[}', 0, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_BRACE and not len(L), "Saw error %d" % e)
        def test8(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'{]', 0, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_BRKT and not len(L), "Saw error %d" % e)
        def test9(self):
            (e,L) = get_comma_sep_exprs_from_balanced_string( r'{123,', 0, debug )
            expL = [ ]
            self.assert_(e==ParserError.SE_NO_CLOSING_PAREN and not len(L), "Saw error %d" % e)


        #############################################
        # test  find_first_simple_id_substr()
        #############################################

        def test_100(self):
            self.assert_( find_first_simple_id_substr('','x',0) == -1 )
            self.assert_( find_first_simple_id_substr('x','',0) == -1 )
            self.assert_( find_first_simple_id_substr('xxx','x',30) == -1 )
            self.assert_( find_first_simple_id_substr('x x x$','x',0) == 0 )
            self.assert_( find_first_simple_id_substr('x x x$','x',1) == 2 )
            self.assert_( find_first_simple_id_substr('x x x$','x',3) == -1 )
            self.assert_( find_first_simple_id_substr('abc$ abc:' ,'abc', 0) == 5 )
            self.assert_( find_first_simple_id_substr('abc$ abcabc' ,'abc', 0) == -1 )
            self.assert_( find_first_simple_id_substr('abc$ abcabc' ,'abc', 8) == -1 )

    unittest.main()
