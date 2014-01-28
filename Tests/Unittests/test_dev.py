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
import VeriParser.BitVector

def simple_test(program, debug=0, sim_end_time_fs=100000):
    ''' Given a string (verilog program) in program, compile and run it.
    '''

    preProcess = PreProcess();
    preProcess.load_source_from_string(program)
    preProcess.preprocess_text()  # comments and includes and defines and undefs

    if debug: preProcess.print_text() 

    data = ''.join(preProcess.text)
    parser = new_Verilog_EBNF_parser()
    try:
        parsed_data = parser.parseString(data, True)
    except Exception as e:
        print `e`

    # need Global gbl for tracking all signals and events
    gbl = VeriParser.Global.Global( sim_end_time_fs = sim_end_time_fs, \
                                    debug = debug )  


    # Construct sim structures from parse tree

    gbl.process_parse_tree(parsed_data)

    # run sim

    gbl.run_sim(debug)

    return gbl



class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    
    def check_uniq_sig_exists(self, gbl, uniq_sig, bit_width=None, int_value=None):
        self.assert_(uniq_sig in gbl.uniq_sigs,
                    "Expected uniq signal name '%s' was not found in global list. " % uniq_sig )
        if bit_width:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.num_bits == bit_width, \
                    "Expected signal '%s' to have bitwidth %d but saw %d.\n" % \
                    ( uniq_sig, bit_width, gbl.uniq_sigs[uniq_sig].bit_vec.num_bits) )

        if int_value != None:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.bin_data == int_value, \
                    "Expected signal '%s' to have value %d but saw %d.\m" %        \
                    (  uniq_sig, int_value, gbl.uniq_sigs[uniq_sig].bit_vec.bin_data ) )



    def test1(self, debug=0):

        data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
        gbl = simple_test(data, debug)
        self.check_uniq_sig_exists( gbl, 'my_module.r1_1', bit_width=32 )
        self.check_uniq_sig_exists( gbl, 'my_module.r2_2', bit_width=32 )


    def test2(self, debug=0):

        data = '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg r;\n initial r=0; always begin\n #1 r = r+1 ;\n end\n endmodule'
        gbl = simple_test(data, debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 32, int_value=100 )

    def test2a(self, debug=0):

        data = '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg [63:0] r;\n initial r=0; always begin\n #1 r = r+1000000000 ;\n end\n endmodule'
        gbl = simple_test(data, debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 64, int_value=100000000000L )


    def test3(self, debug=0):

        data = """module my_module ( port1, port2) ; reg [31:0] r,aaa; initial begin r = 1; begin aaa = 3; end end endmodule """
        gbl = simple_test(data, debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   32, int_value=1 )
        self.check_uniq_sig_exists( gbl, 'my_module.aaa_2', 32, int_value=3 )




    def perf_1(self, debug=VeriParser.Global.Global.DBG_STATS):

        data =  '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg r, s;\n'
        data += ' initial begin r=0; s=0; end\n'
        data += ' always begin\n s =s+1;\n #1 r = r+1 ;\n end\n endmodule'
        gbl = simple_test(data, debug, sim_end_time_fs=1000000000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 32, int_value=1000000 )
        self.check_uniq_sig_exists( gbl, 'my_module.s_2', 32, int_value=1000001 )




if __name__ == '__main__':
    # unittest.main()

    perf = unittest.TestSuite()
    perf.addTest( test_dev('perf_1' ))

    fast = unittest.TestSuite()
    fast.addTest( test_dev('test1' ))
    fast.addTest( test_dev('test2' ))
    fast.addTest( test_dev('test2a' ))
    fast.addTest( test_dev('test3' ))


    # unittest.TextTestRunner().run(fast)
    unittest.TextTestRunner().run(perf)
