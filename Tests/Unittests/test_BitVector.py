##################################################
#
# tests BitVector
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Play/Python/PyVeri")
from VeriParser.BitVector import *


class test_BitVector(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self):pass
    def checkResults(self, exp_e, e, exp_b, b):
        self.assert_( e==exp_e and b == exp_b, 
                     "Exp err %d, saw %d.\n\tExp body '%s' saw '%s'" % (exp_e, e, exp_b, b) )

    def test1(self):
        for i in xrange(256):
            num_bits = i+1
            bv = BitVector(num_bits)
            self.assert_(bv.num_bits == num_bits)
            self.assert_(bv.bin_data == 0)
            self.assert_(bv.is_x == ( 1 << num_bits ) - 1)

    def test2(self):
        for i in xrange(256):
            num_bits = i+1
            bv = BitVector(num_bits, 1<<i)
            self.assert_(bv.num_bits == num_bits)
            self.assert_(bv.bin_data == 1<<i)
            self.assert_(bv.is_x == 0)

    def test3(self):
        bv = BitVector(32, 0x12345678)
        for i in xrange(31,0,-1):
            bv.set_num_bits(i)
            mask = ( 1 << i ) - 1 
            self.assert_(bv.num_bits == i)
            self.assert_(bv.bin_data == (0x12345678 & mask ))
            self.assert_(bv.is_x == 0)

        bv = BitVector(32)
        for i in xrange(31,0,-1):
            bv.set_num_bits(i)
            mask = ( 1 << i ) - 1 
            self.assert_(bv.num_bits == i)
            self.assert_(bv.is_x == mask)


    def test4(self):
        bv = BitVector(32, 0x12345678)
        for bitlen in xrange(1,32):
            mask = ( 1 << bitlen ) - 1
            for start in xrange(0,(32-bitlen+1)):
                end = start + bitlen - 1
                exp_d = ( 0x12345678 >> start ) & mask
                bv_d = bv.get_bin_data( self_max=end, self_min=start)
                # print "bv.get_bin_data(%d,%d) == 0x%x.   Exp=0x%x" % (end, start, bv_d, exp_d)
                self.assert_(bv_d == exp_d," exp:0x%x\nsaw:0x%x   [%d,%d]" % (exp_d, bv_d, end,start))


    def test5(self):
        for numbits in xrange(1,256):
            bv = BitVector(256, 1<<(numbits-1) )
            other = BitVector(numbits, 1<<(numbits-1))
            self.assert_( bv.is_same_when_extended( other ))
            other = BitVector(numbits, 1<<(numbits))
            self.assert_( bv.is_same_when_extended( other ) == False )
            other = BitVector(1, 1)
            self.assert_(bv.is_same_when_extended( other, self_max = numbits-1, self_min = numbits-1 ))
            if numbits > 1: self.assert_( bv.is_same_when_extended( other, self_max = numbits-1, self_min = 0 ) == False)


    def test6(self):
        bv = BitVector(256, val_int=0)
        for numbits in xrange(256,0,-1):
            other = BitVector(numbits, 1<<(numbits-1))
            bv.update_from(other)
            self.assert_( bv.is_same_when_extended( other ))

        other1 = BitVector(8,val_int=0xff)
        for start in xrange(0,256-8):
            bv = BitVector( 256, val_int=0 )
            bv.update_from(other1, self_max = start+7, self_min = start)
            expd = 0xff << start
            bvd = bv.get_bin_data()
            self.assert_(bvd == expd, "\nexpd=0x%x\nbv  =0x%x" % (expd, bvd))

            
        c = 0x12345678abcd112212345678abcd1122
        c2 = 0x556611ff
        other2 = BitVector(32,c2)
        for start in xrange(0,256-32):
            bv = BitVector( 256, c )
            bv.update_from(other2, self_max = start+31, self_min = start)
            expd = c & ~(0xffffffff << start) | ( c2 << start)
            bvd = bv.get_bin_data()
            self.assert_(bvd == expd, "\nstart=%d\nexpd=0x%x\nbv  =0x%x" % (start, expd, bvd))




if __name__ == '__main__':
    unittest.main()

