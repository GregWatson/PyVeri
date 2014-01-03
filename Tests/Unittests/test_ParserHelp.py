##################################################
#
# tests ParserHelp - helper functions
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Play/Python/PyVeri")

from VeriParser.ParserHelp import *

debug = 0

class test_ParserHelp(unittest.TestCase):
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
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'(123 , ["ab{}c"], f(1,2,"ab")[0:4], )', 0, debug )
        expL = [ '123', '["ab{}c"]', 'f(1,2,"ab")[0:4]','' ]
        self.assert_(e==0, "Saw error %d" % e)
        self.assert_(p==36,"bad pos returned:%d" % p)
        self.checkList(L, expL)

    def test2(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'(,  )', 0, debug )
        expL = [ '', '' ]
        self.assert_(e==0, "Saw error %d" % e)
        self.assert_(p==4,"bad pos returned:%d" % p)
        self.checkList(L, expL)

    def test3(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 11, debug )
        expL = [ 'abc{,}', '123' ]
        self.assert_(e==0, "Saw error %d" % e)
        self.assert_(p==27,"bad pos returned:%d" % p)
        self.checkList(L, expL)

    def test4(self):
        print "\nExpect Internal ERROR:"
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 99, debug )
        expL = [ ]
        self.assert_(e==ParserError.SE_SYNTAX_ERROR and not len(L), "Saw error %d" % e)

    def test5(self):
        print "\nExpect Internal ERROR:"
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'some start ( abc{,}  , 123 )xxxx', 2, debug )
        expL = [ ]
        self.assert_(e==ParserError.SE_SYNTAX_ERROR and not len(L), "Saw error %d" % e)

    def test6(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'[)', 0, debug )
        self.assert_(p==0,"bad pos returned:%d" % p)
        expL = [ ]
        self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_PAREN and not len(L), "Saw error %d" % e)
    def test7(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'[}', 0, debug )
        self.assert_(p==0,"bad pos returned:%d" % p)
        expL = [ ]
        self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_BRACE and not len(L), "Saw error %d" % e)
    def test8(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'{]', 0, debug )
        self.assert_(p==0,"bad pos returned:%d" % p)
        expL = [ ]
        self.assert_(e==ParserError.SE_UNBALANCED_CLOSING_BRKT and not len(L), "Saw error %d" % e)


    def test9(self):
        (e,p,L) = get_comma_sep_exprs_from_balanced_string( r'{123,', 0, debug )
        self.assert_(p==0,"bad pos returned:%d" % p)
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

if __name__ == '__main__':
    unittest.main()
