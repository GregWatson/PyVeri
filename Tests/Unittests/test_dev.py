##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Play/Python/PyVeri")
from VeriParser.PreProcess import *
from VeriParser.pyParseVerilogBNF import *
import VeriParser.Global, VeriParser.VeriModule

def simple_test(program, debug):
    ''' Given a string (verilog program) in program, compile and run it.
    '''

    preProcess = PreProcess();
    preProcess.load_source_from_string(program)
    preProcess.preprocess_text()  # comments and includes and defines and undefs

    preProcess.print_text() 

    data = ''.join(preProcess.text)
    parser = new_Verilog_EBNF_parser()
    try:
        parsed_data = parser.parseString(data, True)
    except Exception as e:
        print `e`

    gbl = VeriParser.Global.Global()  # needed for tracking all signals and events

    # Construct sim structures from parse tree

    gbl.process_parse_tree(parsed_data)

    # run sim

    gbl.run_sim(debug)

    return gbl



class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    
    def check_uniq_sig_exists(self, gbl, uniq_sig, bit_width=None):
        self.assert_(uniq_sig in gbl.uniq_sigs,
                    "Expected uniq signal name '%s' was not found in global list. " % uniq_sig )
        if bit_width:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.num_bits == bit_width, \
                    "Expected signal '%s' to have bitwidth %d but saw %d.\n" % \
                    ( uniq_sig, bit_width, gbl.uniq_sigs[uniq_sig].bit_vec.num_bits) )


    def test1(self, debug=0):

        data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
        gbl = simple_test(data, debug)
        self.check_uniq_sig_exists( gbl, 'my_module.r1_1', 32 )
        self.check_uniq_sig_exists( gbl, 'my_module.r2_2', 32 )




if __name__ == '__main__':
    # unittest.main()

    data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
    #data = '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg r;\n initial r=0; always begin\n #1.345 r = r+1 ;\n end\n endmodule'
    #data = """module my_module ( port1, port2) ; reg [31:0] r,aaa; initial begin r = 1; begin aaa = 3; end end endmodule """
    #data = '`timescale 1 ps / 100 fs \n module my_module ( port1, port2) ;\n  reg [31:0] r1;\n initial r1 = 1;\n endmodule'
    #data = '`timescale 1 fs / 100 fs'

    fast = unittest.TestSuite()
    fast.addTest( test_dev('test1' ))
    unittest.TextTestRunner().run(fast)
