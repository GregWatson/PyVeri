##################################################
#
# tests PreProcess
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Play/Python/PyVeri")
from VeriParser.PreProcess import *



debug = 0

class test_PreProcess(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self):pass

    def test1(self):
        obj = PreProcess();

        obj.text = [ '// hello Greg', 'line 2', 'Line 3 // after line 2 // but not this',
        'line /* not this*/4', '"line 5 /* not a comment; a // string."',
        '/* comment, not a "string"', 'still a comment.*/', 
        'li/* */ne/* comment */ 8 // comment', 'line 9 bad string ends in dub quotes"',
        '"line \\"10\\" in quotes like this:\\""', '/* short in long // */',
        'line 12 // short c before long /* */', '/**/ line 13 // ultra short long comment',
        'line 14 /* long comment ending at EOL */',
        'line 15 /* lc starts here', 'and goes on thru 16 // ', 'ends here */ line 17 /* */',
        'last line' ]

        good_LoS = [ '','line 2','Line 3 ','line 4','"line 5 /* not a comment; a // string."'
                    ,'','','line 8 ','line 9 bad string ends in dub quotes"'
                    ,'"line \\"10\\" in quotes like this:\\""','','line 12 ',' line 13 ','line 14 '
                    ,'line 15 ','',' line 17 ',
                    'last line']

        err = obj.strip_comments(obj.text)
        self.assert_(err==0, "test1 Unexpected err %d returned from strip_comments()" % err )
        for ix  in xrange(len(obj.text)):
            self.assert_( obj.text[ix] == good_LoS[ix] ,
                        "test1 Line %d saw '%s'\nbut expected: '%s'" % (ix, obj.text[ix], good_LoS[ix]) )

    def test2(self):
        obj = PreProcess();
        obj.text = ['/* comment runs on beyond file ...', '....']
        err = obj.strip_comments(obj.text)
        self.assert_(err == ParserError.ERR_UNTERMINATED_COMMENT ,
                    "Expected ParserError.ERR_UNTERMINATED_COMMENT (errnum %d) but saw %d." % \
                    ( ParserError.ERR_UNTERMINATED_COMMENT, err) )

    def test3(self):
        test_id = 3

        obj = PreProcess()
        src_text = ['line 1', 'line 2', 'line 3']
        exp_text = ['line 1', 'line 2', 'line 1', 'line 2', 'line 3', 'line 3']

        obj.insert_source_from_string_array_to_line(src_text, 'filename', 0)
        obj.insert_source_from_string_array_to_line(src_text, 'filename', 2)

        self.assert_( len(obj.text) == len(exp_text) , 
                      "test %d: lengths of exp text not same as actual: %d and %d" % \
                       (test_id, len(exp_text), len(obj.text)) )
        for ix  in xrange(len(obj.text)):
            self.assert_( obj.text[ix] == exp_text[ix] ,
                      "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], exp_text[ix]) )

    def test4(self):
        test_id = 4

        obj = PreProcess()
        obj.debug = 0
        f = "../data/simple2.v"

        exp_text = ['line 1', 'line 2', 'line 1', 'line 2', 'line 3']

        obj.load_source_from_file(f)
        obj.preprocess_text(debug=0)

        self.assert_( len(obj.text) == len(exp_text) ,
                      "test %d lengths of exp text not same as actual: %d and %d" % \
                      (test_id, len(exp_text), len(obj.text)) )
        for ix  in xrange(len(obj.text)):
            self.assert_( obj.text[ix] == exp_text[ix], 
                       "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], exp_text[ix]) )

    def test5(self):
        test_id = 5

        obj = PreProcess()
        obj.debug = 0
        f = "../data/simple3.v"

        exp_text = ['' for i in xrange(24)] 
        exp_text[12] = '((a+b)+d[10:0])'
        exp_text[15] = '((3+{{2}[5:2]})+99.6)+(5+9) '
        exp_text[18] = '$display($time, "a string // really!");'

        obj.load_source_from_file(f)

        print "\nNote: Expect Redefined Macro warning"
        print "Note: Expect WARNING: Macro not previously defined: `undef macro 'm4' in ..."

        err = obj.preprocess_text()
        self.assert_( err == ParserError.ERR_UNTERMINATED_MACRO ,
            "test %d expected to return err %d but saw %d" % 
            (test_id, ParserError.ERR_UNTERMINATED_MACRO, err ) )

        r = self.assert_( len(obj.text) == len(exp_text), 
                "test %d lengths of exp text not same as actual: %d and %d" % \
                    (test_id, len(exp_text), len(obj.text)) )
        #if not r: print obj.text
        for ix  in xrange(len(obj.text)):
            self.assert_ ( obj.text[ix] == exp_text[ix] ,
                    "test %d Line %d saw\n'%s'\nbut expected:\n'%s'" % (test_id, ix, obj.text[ix], exp_text[ix]) )


if __name__ == '__main__':
    unittest.main()

