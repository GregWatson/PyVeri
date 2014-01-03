##################################################
#
# tests VMacro
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Play/Python/PyVeri")
from VeriParser.VMacro import *


debug   = 0
m_fxy   = VMacro('f(x,y) (x+y)')
m_fx    = VMacro('f(x) x xxx x')
m_fxy2  = VMacro('f(x,y) (x+y)-$x+y$*zzy')
m_fx_xx = VMacro('f(x,xx) (x+xx)-(xx+x)xxx')

class test_VMacro(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self):pass
    def checkResults(self, exp_e, e, exp_b, b):
        self.assert_( e==exp_e and b == exp_b, 
                     "Exp err %d, saw %d.\n\tExp body '%s' saw '%s'" % (exp_e, e, exp_b, b) )

    def test1(self):
        (e,b) = m_fxy.subst_args_in_body(['x','y'])
        (exp_e, exp_b) = ( 0, '(x+y)' )
        self.checkResults(exp_e, e, exp_b, b)

    def test2(self):
        (e,b) = m_fxy.subst_args_in_body(['abc','def'])
        (exp_e, exp_b) = ( 0, '(abc+def)' )
        self.checkResults(exp_e, e, exp_b, b)

    def test3(self):
        (e,b) = m_fx.subst_args_in_body(['abc'])
        (exp_e, exp_b) = ( 0, 'abc xxx abc' )
        self.checkResults(exp_e, e, exp_b, b)


    def test4(self):
        (e,b) = m_fxy.subst_args_in_body(['abc'])
        (exp_e, exp_b) = ( ParserError.SE_MACRO_HAS_WRONG_NUMBER_PARAMS, '' )
        self.checkResults(exp_e, e, exp_b, b)

    def test5(self):
        (e,b) = m_fxy.subst_args_in_body(['(yyy + y)','x'])
        (exp_e, exp_b) = ( 0, '((yyy + y)+x)' )
        self.checkResults(exp_e, e, exp_b, b)


    def test6(self):
        (e,b) = m_fxy2.subst_args_in_body(['abc', 'def'])
        (exp_e, exp_b) = ( 0, '(abc+def)-$x+y$*zzy' )
        self.checkResults(exp_e, e, exp_b, b)

    def test7(self):
        (e,b) = m_fx_xx.subst_args_in_body(['abc', 'b'])
        (exp_e, exp_b) = ( 0, '(abc+b)-(b+abc)xxx' )     # real answer if we do the right thing.
        self.checkResults(exp_e, e, exp_b, b)



if __name__ == '__main__':
    unittest.main()

