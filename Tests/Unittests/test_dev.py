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
import VeriParser.VeriExceptions
import VeriParser.VeriCompile

def simple_test(program, debug=0, opt_vec=0, sim_end_time_fs=100000, top_module=''):
    ''' Given a string (verilog program) in program, compile and run it.
        If you have a top level module then name it, otherwise it will
        build all top level modules.
    '''
    gbl = VeriParser.VeriCompile.compile_string_as_string(
            program=program, 
            debug=debug, 
            opt_vec=opt_vec, 
            sim_end_time_fs = sim_end_time_fs,
            top_module = top_module
          )

    if not gbl:
        print "Hmmm. Syntax error?"
        sys.exit(1)

    # run sim

    gbl.run_sim(debug, opt_vec)
    return gbl

    
class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    
    def check_uniq_sig_exists(self, gbl, uniq_sig, bit_width=None, int_value=None, is_x=None):
        self.assert_(uniq_sig in gbl.uniq_sigs,
                    "Expected uniq signal name '%s' was not found in global list. " % uniq_sig )
        if bit_width:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.num_bits == bit_width, \
                    "Expected signal '%s' to have bitwidth %d but saw %d.\n" % \
                    ( uniq_sig, bit_width, gbl.uniq_sigs[uniq_sig].bit_vec.num_bits) )

        if int_value != None:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.bin_data == int_value, \
                    "Expected signal '%s' to have value 0x%x but saw 0x%x.\m" %        \
                    (  uniq_sig, int_value, gbl.uniq_sigs[uniq_sig].bit_vec.bin_data ) )

        if is_x != None:
            self.assert_(gbl.uniq_sigs[uniq_sig].bit_vec.is_x == is_x, \
                    "Expected signal '%s' to have is_x set to  0x%x but saw 0x%x.\m" %        \
                    (  uniq_sig, is_x, gbl.uniq_sigs[uniq_sig].bit_vec.is_x ) )




    def perf_1(self, opt_vec=2, debug=VeriParser.Global.Global.DBG_STATS):

        data =  '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg [31:0] r, s;\n'
        data += ' initial begin r=0; s=0; end\n'
        data += ' always begin\n s =s+1;\n #1 r = r+1 ;\n end\n endmodule'
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=1000000000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 32, int_value=1000000 )
        self.check_uniq_sig_exists( gbl, 'my_module.s_2', 32, int_value=1000001 )




    def test1(self, debug=0, opt_vec=2):

        data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug)
        self.check_uniq_sig_exists( gbl, 'my_module.r1_1', bit_width=32 )
        self.check_uniq_sig_exists( gbl, 'my_module.r2_2', bit_width=32 )


    def test2(self, debug=0, opt_vec=2):

        data = '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg r;\n initial r=0; always begin\n #1 r = r+1 ;\n end\n endmodule'
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 1, int_value=0 )


    def test2a(self, debug=0, opt_vec=2):

        data = '`timescale 1 ps / 100 fs\nmodule my_module ( port1, port2) ;\n reg [63:0] r;\n initial r=0; always begin\n #1 r = r+1000000000 ;\n end\n endmodule'
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 64, int_value=100000000000L )



    def test2b(self, opt_vec=2, debug=0): #VeriParser.Global.Global.DBG_EVENT_LIST):

        data = '''
`timescale 1 ps / 100 fs
module my_module ( port1, port2) ;
reg [63:0] r;
wire [3:0] w;
assign w = 15;
initial r = 0; 
always begin 
  #1 r[63:60] = w[3:0] ;
     r[3:2]   = w[0] ; 
end
endmodule
'''
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=2100)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 64, int_value=0xf000000000000004L )


    def test3(self, debug=0, opt_vec=2):

        data = """module my_module ( port1, port2) ; reg [31:0] r,aaa; initial begin r = 1; begin aaa = 3; end end endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   32, int_value=1 )
        self.check_uniq_sig_exists( gbl, 'my_module.aaa_2', 32, int_value=3 )


    def test4(self, debug=0, opt_vec=2):

        data = """
module my_module ( p) ; 
reg r;\nwire w;
assign w = r;
initial begin   r = 1; 
   #10 r = 0; end 
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   1, int_value=0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w_2',   1, int_value=0 )


    def test4a(self, opt_vec=0, debug= VeriParser.Global.Global.DBG_EVENT_LIST ):

        data = """
module my_module ( p) ;
reg  [3:0] r;  
wire [3:0] w,x;
assign x = 3, w = r + x; 
initial begin   r = 1;   
            #10 r = 0; 
end
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   4, int_value=0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w_2',   4, int_value=3 )
        self.check_uniq_sig_exists( gbl, 'my_module.x_3',   4, int_value=3 )


    
    def test4b(self, debug=0, opt_vec=2): # VeriParser.Global.Global.DBG_EVENT_LIST ):
        ''' This is an infinite loop test. 
            Need to catch VeriExceptions.RuntimeInfiniteLoopError
        '''

        data = """   // Test infinite loop.
module my_module ( p) ;
reg  [3:0] r;  
wire [3:0] w;
assign w = r + w; 
initial begin   r = 1;   end   endmodule """
        try:
            gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        except  VeriParser.VeriExceptions.RuntimeInfiniteLoopError:
            print "RuntimeInfiniteLoopError exception caught, as expected."


    def test4c(self, debug=0, opt_vec=2): # VeriParser.Global.Global.DBG_EVENT_LIST ):
        ''' This is an infinite loop test. 
            Need to catch VeriExceptions.RuntimeInfiniteLoopError
        '''

        data = """   // Test infinite loop.
module my_module ( p) ;
reg  [31:0] r;  
wire [31:0] w1,w2;

assign w1 = r + w2, w2 = r + 1; 
initial r = 1;
always begin #1 r = w1; end   // r <= 2*r + 1

endmodule """

        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=16)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1', 32, int_value=131071 )



    def test4d(self, debug=0, opt_vec=2):  # net id range

        data = """
module my_module ( p) ; 
reg [3:0] r;\nwire [7:0] w;
wire [7:0] w2;
assign w[7:4] = r;
assign w2[7:6] = 0, w2[5:2] = ~r;
initial begin   r = 1; 
   #10 r = 5; end 
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   4, int_value=5 )
        self.check_uniq_sig_exists( gbl, 'my_module.w_2',   8, int_value=80, is_x=0xf )
        self.check_uniq_sig_exists( gbl, 'my_module.w2_3',  8, int_value=40, is_x=0x3 )



    def test4e(self, debug=0, opt_vec=2):  # net concatenation

        data = """
module my_module ( p) ; 
reg [7:0] r;
wire w2,w3;
wire [11:0] w4;
assign { w4[7:2] , {w3, w2} } = r;
initial begin   r = 2; 
   #10 r = 65; end 
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   8, int_value=65, is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w2_2',  1, int_value=1,  is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w3_3',  1, int_value=0,  is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w4_4', 12, int_value=64, is_x=0xf03 )


    def test4f(self, debug=0, opt_vec=2):  # bit assign

        data = """
module my_module ( p) ; 
reg [7:0] r;
wire w2,w3;
wire [11:0] w4;
assign { w4[7], w4[6:5], w4[4] , w4[3:2] , {w3, w2} } = r;
initial begin   r = 2; 
    #1 r =   0;
    #1 r = 255;
    #8 r =  65; 
end 
// $monitor(w4);
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.r_1',   8, int_value=65, is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w2_2',  1, int_value=1,  is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w3_3',  1, int_value=0,  is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.w4_4', 12, int_value=64, is_x=0xf03 )


    def test4g(self, debug=0, opt_vec=2):  # reg bit assign

        data = """
module my_module ( p) ; 
reg zero, one;
reg [3:0] tgt;
initial begin   
       zero = 0; one = 1;
       tgt[0] = zero;
       tgt[1] = one;
       tgt[2] = zero;
       tgt[3] = one;
end 
$monitor(tgt);
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.tgt_3',  4, int_value=0xa, is_x=0x0 )


    def test4h(self, debug=0, opt_vec=2):  # reg range assign

        data = """
module my_module ( p) ; 
reg [1:0] two;
reg [3:0] tgt;
initial begin   
       two = 2;
       tgt[1:0] = two;
       tgt[3:2] = two;
end 
$monitor(tgt);
endmodule """
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=100000)
        self.check_uniq_sig_exists( gbl, 'my_module.two_1',  2, int_value=0x2, is_x=0x0 )
        self.check_uniq_sig_exists( gbl, 'my_module.tgt_2',  4, int_value=0xa, is_x=0x0 )


    def test5(self, opt_vec=2, debug= 0): #VeriParser.Global.Global.DBG_EVENT_LIST ):
        ''' two top level modules '''

        data = """
module invert (in, out) ;
input in;
output out;
reg  out;  
always #1 out = ~in;
endmodule 

module top; reg top_r; wire top_w;
initial top_r = 0 ;
always #10 top_r = ~top_r;
endmodule

"""

        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=2)
        self.check_uniq_sig_exists( gbl, 'invert.in_1', 1 )
        self.check_uniq_sig_exists( gbl, 'invert.out_2', 1 )



    def test5a(self, opt_vec=2, debug= VeriParser.Global.Global.DBG_EVENT_LIST ):
        ''' simple module instantiation test '''

        data = """
module invert (in, out) ;
input in;
output out;
reg  out;  
always #1 out = ~in;
endmodule 

module top; reg top_r; wire top_w;
initial top_r = 0 ;
always #10 top_r = ~top_r;
invert inv_mod1(.in(top_r), .out(top_w));
// invert inv_mod1(.in(top_r), .out(top_w)) , inv_mod2(.in(top_r), .out(top_w));
$monitor(top_r, top_w);
endmodule

"""
        gbl = simple_test(data, opt_vec=opt_vec, debug=0, sim_end_time_fs=32, top_module='top')
        self.check_uniq_sig_exists( gbl, 'top.top_r_4', 1 , int_value=1)
        self.check_uniq_sig_exists( gbl, 'top.top_w_5', 1 , int_value=0)




    def test5b(self, opt_vec=2, debug=0): # VeriParser.Global.Global.DBG_EVENT_LIST ):
        ''' simple module instantiation test with signal ranges'''

        data = """
module invert (in, out) ;
input in;
output out;
reg  out;  
always #1 out = ~in;
endmodule 

module top; reg [3:0] top_r; wire [3:0] top_w;
initial top_r = 0 ;
always #10 top_r = ~top_r;
invert inv_mod(.in(top_r), .out(top_w[3:0]));
$monitor(top_r, top_w);
endmodule

"""
        gbl = simple_test(data, opt_vec=opt_vec, debug=debug, sim_end_time_fs=32, top_module='top')
        #self.check_uniq_sig_exists( gbl, 'top.top_r_4', 1 , int_value=1)
        #self.check_uniq_sig_exists( gbl, 'top.top_w_5', 1 , int_value=0)



if __name__ == '__main__':
    # unittest.main()

    perf = unittest.TestSuite()
    perf.addTest( test_dev('perf_1' ))

    fast = unittest.TestSuite()
    fast.addTest( test_dev('test1' ))
    fast.addTest( test_dev('test2' ))
    fast.addTest( test_dev('test2a' ))
    fast.addTest( test_dev('test2b' ))
    fast.addTest( test_dev('test3' ))
    fast.addTest( test_dev('test4' ))
    fast.addTest( test_dev('test4a' ))
    fast.addTest( test_dev('test4b' ))
    fast.addTest( test_dev('test4c' ))
    fast.addTest( test_dev('test4d' ))
    fast.addTest( test_dev('test4e' ))
    fast.addTest( test_dev('test4f' ))
    fast.addTest( test_dev('test4g' ))
    fast.addTest( test_dev('test4h' ))
    fast.addTest( test_dev('test5' ))
    fast.addTest( test_dev('test5a' ))
    # fast.addTest( test_dev('test5b' ))

    single = unittest.TestSuite()
    single.addTest( test_dev('test2b' ))

    #unittest.TextTestRunner().run(fast)
    #unittest.TextTestRunner().run(perf)
    unittest.TextTestRunner().run(single)
