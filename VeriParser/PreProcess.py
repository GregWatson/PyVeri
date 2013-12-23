##################################################
#
# PreProcess - class to perform preprcoessing on a raw source file
#
##################################################

import ParserError, re
from SourceText import SourceText
from VMacro import VMacro
from ParserHelp import *

import sys

''' Preprocess a source verilog file:

    - strip comments but preserve lines.
    - process `include "filename" commands: insert file into text but 
      track line numbers back to original file.
    - process `define and corresponding use of a `define'd macro.
      (Note: macros may invoke other macros, and macros can have params)

    See detailed comments at end of file.
'''

class PreProcess(SourceText):

    def __init__(self):
        
        super(PreProcess, self).__init__();


    def preprocess_text(self):
        ''' Preprocess self.text. Return error if one occurs, else 0.
        '''
        err_code = self.strip_comments(self.text)
        if (err_code): return err_code
        err_code = self.preprocess_include_and_define()
        if (err_code): return err_code
        return 0

    @staticmethod       
    def strip_comments(text):
        '''
        Input: verilog text in text
               Strings must not end in CR (should have been stripped).
        Output: error code (0=ok)
        Effect: text is modified in-place.
        '''
        NONE = 0
        IN_LONG = 1

        state = NONE

        for line_num, line in enumerate(text):
            start = 0

            while ( start < len(line) ) :
                if state == NONE:
                    # Look for either // or /*
                    sc_ix = line.find('//',start)   # short comment location
                    lc_ix = line.find('/*',start)   # long comment location
                    # If we have neither then we are done for this line.
                    if ( sc_ix == -1 and lc_ix == -1 ) : 
                        text[line_num] = line
                        break
                    s_ix  = line.find('"',start)   # double quote that starts a string.

                    # see which comes first
                    sc_first = ( sc_ix >= 0 ) and                                \
                               ( ( s_ix == -1    or ( s_ix > sc_ix ) ) and
                                 ( lc_ix == -1 ) or ( lc_ix > sc_ix ) )
                    if sc_first:
                        line = line[0:sc_ix]
                        text[line_num] = line
                        break

                    # now check string ("....")
                    string_first = ( s_ix >= 0 ) and                            \
                                      ( lc_ix == -1 or ( lc_ix > s_ix ) )
                    if string_first:
                        # string starts before any comment. Advance to next " 
                        s_ix = line.find('"',s_ix+1)
                        if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                            text[line_num] = line
                            break
                        # if char before " is \ then the " doesnt count (it's \")
                        while s_ix != -1 and line[s_ix - 1] == '\\' :
                            s_ix = line.find('"',s_ix+1)
                        if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                            text[line_num] = line
                            break
                        start = s_ix + 1
                        if (start >= len(line) ) :
                            text[line_num] = line
                            break
                        continue

                    # Must be a long comment.
                    # If the long comment ends this line then we strip it out
                    # and go round again.
                    e_ix = line.find('*/',lc_ix+2)
                    if e_ix >= 0:
                        line = line[0:lc_ix] + line[e_ix+2:]
                        start = lc_ix
                        if ( start >= len(line) ):
                            text[line_num] = line
                            break
                    else: # didnt see end of comment - must run on.
                        line = line[0:lc_ix]
                        text[line_num] = line
                        state = IN_LONG
                        break

                else: # state is IN_LONG - look for first */ that ends the comment.
                    lc_ix = line.find('*/')
                    if lc_ix == -1 : # did not see */ in this line - comment continuing
                        text[line_num] = ''
                        break
                    # found */
                    line = line[lc_ix+2:]
                    if len(line) == 0:
                        text[line_num] = ''
                    state = NONE

        if state == IN_LONG:
            return ParserError.ERR_UNTERMINATED_COMMENT
        else:
            return 0

    def add_macro(self, macro_text, line_num, filename):
        ''' macro_text is a text string defined in filename at line line_num.
            Create macro object and add it to list of known macros. 
            Do not interpolate any `macro used in the definition - they are 
            interpolated when macro is used.
        '''
        macro = VMacro(macro_text, line_num, filename)
        if macro.name in self.macros:
            orig_macro = self.macros[macro.name]
            print "WARNING: redefined macro '%s' in file %s at line %d." \
                % (macro.name, macro.filename, macro.line_num)
            print "         Prev defined in file %s at line %d." \
                % (orig_macro.filename, orig_macro.line_num)
        
        self.macros[macro.name] = macro
        if self.debug: print "Added macro:", macro


    def do_macro_substitution(self, line, line_num, filename):
        ''' Do a single macro substitution (if any).
            Note: assumes that first backtick is a macro subst - i.e.
                if it was a `include or something else then you better
                have dealt with it already.
            Returns modified line.
        '''
        tick_pos = line.find('`')
        if tick_pos == -1: return line
        # get macro name (after the tick)
        (err, macro_name) = get_simple_identifier_at_offset(line, tick_pos+1)
        if err:
            ParserError.report_syntax_err(ParserError.SE_ID_EXPECTED_AFTER_TICK, line_num, filename)
        if macro_name not in self.macros:
            ParserError.report_syntax_err(ParserError.SE_MACRO_NOT_DEFINED, line_num, filename)

        # Must differentiate between macro with args and without.
        # A macro with args must be followed by '(' immediately after name.

        nxt_pos = tick_pos + len(macro_name) + 1

        if nxt_pos >= len(line) or line[nxt_pos] != '(':  # simple macro (no args)

            line = line[0:tick_pos] + self.macros[macro_name].text + line[nxt_pos:]

        else: # macro with args

            (err, arg_end_pos, argL) = get_comma_sep_exprs_from_balanced_string(line, nxt_pos)
            if err:
                ParserError.report_syntax_err(err, line_num, filename)

            macro = self.macros[macro_name]

            # get the original macro body, replacing formal params with actual args.

            (err,new_body) = macro.subst_args_in_body(argL)
            if err: ParserError.report_syntax_err(err, line_num, filename)

            line = line[0:tick_pos] + new_body + line[arg_end_pos+1:]

        return line


    def insert_include_file(self, inc_file, index):
        ''' insert the specified `include file in self.text at the
            location specified by index. 
            Remove the old line (the `include line)
            Return err or 0
        '''
        if (self.debug): print "DBG: Including `include file '%s'" % inc_file
        (err, new_text) = self.load_text_from_file_and_strip_CR(inc_file)
        if err: return err

        err = self.strip_comments(new_text)
        if not err:  # replace this line with new text into self.text
            err = self.insert_source_from_string_array_to_line(new_text, inc_file, index)
        if err: return err
        self.delete_text_range( first=index+len(new_text)  )

        if (self.debug): 
            print "DBG: after including file",inc_file,"text is now:"
            self.print_text()   

        return 0


    def preprocess_include_and_define(self):
        ''' self.text already stripped of comments.
            Process `include lines as well as `define macros.
            Process macro instantiations (replace them with their definitions)
            Modifies self.text in place.
            returns 0 or error_num
        '''
        pat_include = re.compile(r'`include\s*"([^"]+)"')
        pat_define  = re.compile(r'`define\s+(.+)')

        text_ix = 0

        while text_ix < len(self.text):

            line     = self.text[text_ix]
            line_num = self.original_line_num[text_ix]
            filename = self.original_file_list[self.original_file_idx[text_ix]]

            while line.find("`") != -1:

                # Look for `include "filename". If found then read the text from that
                # file, strip comments, and insert it into self.text, replacing the
                # current `include line.

                match = pat_include.search(line)

                if match: # it's a `include.
                    inc_file = match.group(1)
                    err = self.insert_include_file( inc_file, text_ix )
                    if err: return err
                    line = self.text[text_ix]  # this line has changed. process it again

                else:
                    # Look for `define              
                    match = pat_define.search(line)

                    if match: # it's a `define, so add the macro
                        def_text     = [ match.group(1) ]

                        self.text[text_ix] = '' # remove text.
                        while def_text[-1].endswith('\\'):    # macro continues to next line
                            def_text[-1] = def_text[-1].rstrip('\\')
                            text_ix += 1
                            if text_ix >= len(self.text): return ParserError.ERR_UNTERMINATED_MACRO
                            def_text.append(self.text[text_ix])
                            self.text[text_ix] = '' # remove text.
                        macro = ''.join(def_text)
                        self.add_macro( macro, line_num, filename )
                        break

                    # Not a keyword, so check for macro substitution.
                    else:
                        self.text[text_ix] = self.do_macro_substitution(line, line_num, filename)
                        line = self.text[text_ix]   # this line has changed. process it again

            text_ix +=1 

        return 0


####################################################
if __name__ == '__main__' :

    import unittest

    debug = 0

    class TestParserHelp(unittest.TestCase):
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
                          "test %d lengths of exp text not same as actual: %d and %d" % \
                           (test_id, len(exp_text), len(obj.text)) )
            for ix  in xrange(len(obj.text)):
                self.assert_( obj.text[ix] == exp_text[ix] ,
                          "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], exp_text[ix]) )

        def test4(self):
            test_id = 4

            obj = PreProcess()
            obj.debug = 0
            f = "../Tests/data/simple2.v"

            exp_text = ['line 1', 'line 2', 'line 1', 'line 2', 'line 3']

            obj.load_source_from_file(f)
            obj.preprocess_text()

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
            f = "../Tests/data/simple3.v"

            exp_text = ['' for i in xrange(21)] 
            exp_text[12] = '((a+b)+d[10:0])'
            exp_text[15] = '((3+{{2}[5:2]})+99.6)+(5+9) '
            exp_text[18] = '$display($time, "a string // really!");'

            obj.load_source_from_file(f)
            print "\nNote: Expect Redefined Macro warning"
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

    unittest.main()
 


''' 
Remove all comments (long and short) but preserve resulting blank lines:

    Watch out for comment chars starting in strings - ignore them.
    Once in a long comment (/* ... */) we ignore everything until we see */
    Short comment ( // ) is to end of line.

'''
