##################################################
#
# PreProcess - class to perform preprcoessing on a raw source file
#
##################################################

import ParserError, re
from SourceText import SourceText
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
            return ParserError.UNTERMINATED_COMMENT
        else:
            return 0


    def preprocess_include_and_define(self):
        ''' self.text already stripped of comments.
            Process `include lines as well as `define macros.
            Process macro instantiations (replace them with their definitions)
            Modifies self.text in place.
            returns 0 or error_num
        '''
        pat_include = re.compile(r'`include\s*"([^"]+)"')

        text_ix = 0

        print self.text

        while text_ix < len(self.text):

            line = self.text[text_ix]

            while line.find('`') != -1:

                # Look for `include "filename". If found then read the text from that
                # file, strip comments, and insert it into self.text, replacing the
                # current `include line.

                match = pat_include.search(line)

                if match: # it's a `include.
                    inc_file = match.group(1)
                    if (self.debug): print "DBG: Including `include file '%s'" % inc_file
                    (err, new_text) = self.load_text_from_file_and_strip_CR(inc_file)
                    if err: return err

                    err = self.strip_comments(new_text)
                    if not err:  # replace this line with new text into self.text
                        err = self.insert_source_from_string_array_to_line(new_text, inc_file, text_ix)
                    if err: return err
                    del self.text[text_ix+len(new_text)]
            
                    line = self.text[text_ix]  # this line has changed. process it again
                    if (self.debug): 
                        print "DBG: after including file",inc_file,"text is now:"
                        self.print_text(self.text)

                # Look for `define                 

            text_ix +=1 

        return 0


####################################################
if __name__ == '__main__' :

    errors  = 0
    test_id = 1

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
    if err:
        print "test %d Unexpected err %d returned from strip_comments()" % (test_id, err)
        errors += 1
    for ix  in xrange(len(obj.text)):
        if (obj.text[ix] != good_LoS[ix]):
            print "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], good_LoS[ix])
            errors += 1

    #-------------------------------------------------
    test_id += 1

    obj.text = ['/* comment runs on beyond file ...', '....']
    err = obj.strip_comments(obj.text)
    if err != ParserError.UNTERMINATED_COMMENT :
        print "Expected ParserError.UNTERMINATED_COMMENT (errnum %d) but saw %d." % \
            ( ParserError.UNTERMINATED_COMMENT, err)
        errors += 1

    #-------------------------------------------------
    test_id += 1

    obj = PreProcess()
    src_text = ['line 1', 'line 2', 'line 3']
    exp_text = ['line 1', 'line 2', 'line 1', 'line 2', 'line 3', 'line 3']

    obj.insert_source_from_string_array_to_line(src_text, 'filename', 0)
    obj.insert_source_from_string_array_to_line(src_text, 'filename', 2)

    if len(obj.text) != len(exp_text) :
        print "test %d lengths of exp text not same as actual: %d and %d" % \
                (test_id, len(exp_text), len(obj.text))
        errors += 1
    else:
        for ix  in xrange(len(obj.text)):
            if (obj.text[ix] != exp_text[ix]):
                print "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], exp_text[ix])
                errors += 1

    #-------------------------------------------------
    test_id += 1

    obj = PreProcess()
    obj.debug = 1
    f = "../Tests/data/simple2.v"

    exp_text = ['line 1', 'line 2', 'line 1', 'line 2', 'line 3']

    obj.load_source_from_file(f)
    obj.preprocess_text()

    if len(obj.text) != len(exp_text) :
        print "test %d lengths of exp text not same as actual: %d and %d" % \
                (test_id, len(exp_text), len(obj.text))
        errors += 1
    else:
        for ix  in xrange(len(obj.text)):
            if (obj.text[ix] != exp_text[ix]):
                print "test %d Line %d saw '%s'\nbut expected: '%s'" % (test_id, ix, obj.text[ix], exp_text[ix])
                errors += 1



    #-------------------------------------------------
    if not errors :
        print "++++ No Errors ++++"
    else:
        print "!!!! Saw %d ERRORS !!!!" % errors




''' 
Remove all comments (long and short) but preserve resulting blank lines:

    Watch out for comment chars starting in strings - ignore them.
    Once in a long comment (/* ... */) we ignore everything until we see */
    Short comment ( // ) is to end of line.

'''
