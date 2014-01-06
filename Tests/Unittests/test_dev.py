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


class test_dev(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self):pass

    def test1(self):

        pass


if __name__ == '__main__':
    # unittest.main()


    preProcess = PreProcess();


    data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
    data = """module my_module ( port1, port2) ; initial begin : block_id reg r; reg aaa; r = 1; aaa = 3; end endmodule """
    data = """module my_module ( port1, port2) ; initial begin : block_id reg r; r = 1; aaa = 3; end endmodule """
    data = '`timescale 1 s / 100 fs \n module my_module ( port1, port2) ;\n  reg [31:0] r1;\n initial r1 = 1;\n endmodule'
    data = '`timescale 1 s / 100 fs'

    preProcess.load_source_from_string(data)
    preProcess.preprocess_text()  # comments and includes and defines and undefs

    preProcess.print_text()

    data = ''.join(preProcess.text)
    parser = new_Verilog_EBNF_parser()
    try:
        parsed_data = parser.parseString(data, True)
    except Exception as e:
        print `e`
        sys.exit(1)

    gbl = VeriParser.Global.Global()  # needed for tracking all signals and events

    # Construct sim structures from parse tree

    gbl.process_parse_tree(parsed_data)

    # run sim

    gbl.run_sim()

    print gbl

