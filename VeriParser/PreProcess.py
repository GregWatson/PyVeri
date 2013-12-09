##################################################

import ParserError

''' Preprocess a source verilog file:

    - strip comments but preserve lines.
    - process `include "filename" commands: insert file into text but 
      track line numbers back to original file.
    - process `define and and corresponding use of a `define'd macro.
      (Note: macros may invoke other macros, and macros can have params)

    See detailed comments at end of file.
'''



def preprocess_list_of_strings(LoS):
'''
    Input: verilog text in a list of strings. 
           Strings must not end in CR (should have been stripped).
    Output: error code (0=ok)
    Effect: Input list of strings is modified in-place.
'''
    NONE = 0
    IN_LONG = 1

    state = NONE

    for line_num, text in enumerate(LoS):
        start = 0
        
        while ( start < len(text) ) :
            if state == NONE:
                # Look for either // or /*
                sc_ix = text.find('//',start)   # short comment location
                lc_ix = text.find('/*',start)   # long comment location
                # If we have neither then we are done for this line.
                if ( sc_ix == -1 and lc_ix == -1 ) : 
                    LoS[line_num] = text
                    break
                s_ix  = text.find('"',start)   # double quote that starts a string.

                # see which comes first
                sc_first = ( sc_ix >= 0 ) and                                \
                           ( ( s_ix == -1    or ( s_ix > sc_ix ) ) and
                             ( lc_ix == -1 ) or ( lc_ix > sc_ix ) )
                if sc_first:
                    text = text[0:sc_ix]
                    LoS[line_num] = text
                    break

                # now check string ("....")
                string_first = ( s_ix >= 0 ) and                            \
                                  ( lc_ix == -1 or ( lc_ix > s_ix ) )
                if string_first:
                    # string starts before any comment. Advance to next " 
                    s_ix = text.find('"',s_ix+1)
                    if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                        LoS[line_num] = text
                        break
                    # if char before " is \ then the " doesnt count (it's \")
                    while s_ix != -1 and text[s_ix - 1] == '\\' :
                        s_ix = text.find('"',s_ix+1)
                    if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                        LoS[line_num] = text
                        break
                    start = s_ix + 1
                    if (start >= len(text) ) :
                        LoS[line_num] = text
                        break
                    continue

                # Must be a long comment.
                # If the long comment ends this line then we strip it out
                # and go round again.
                e_ix = text.find('*/',lc_ix+2)
                if e_ix >= 0:
                    text = text[0:lc_ix] + text[e_ix+2:]
                    start = lc_ix
                    if ( start >= len(text) ):
                        LoS[line_num] = text
                        break
                else: # didnt see end of comment - must run on.
                    text = text[0:lc_ix]
                    LoS[line_num] = text
                    state = IN_LONG
                    break
                        
            else: # state is IN_LONG - look for first */ that ends the comment.
                lc_ix = text.find('*/')
                if lc_ix == -1 : # did not see */ in this line - comment continuing
                    LoS[line_num] = ''
                    break
                # found */
                text = text[lc_ix+2:]
                if len(text) == 0:
                    LoS[line_num] = ''
                state = NONE

    if state == IN_LONG:
        return ParserError.UNTERMINATED_COMMENT
    else:
        return 0






####################################################
if __name__ == '__main__' :

    errors = 0

    LoS = [ '// hello Greg', 'line 2', 'Line 3 // after line 2 // but not this',
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

    err = preprocess_list_of_strings(LoS)
    if err:
        print "Unexpected err %d returned from preprocess_list_of_strings()"
        errors += 1
    for ix  in xrange(len(LoS)):
        if (LoS[ix] != good_LoS[ix]):
            print "Line %d saw '%s'\nbut expected: '%s'" % (ix, LoS[ix], good_LoS[ix])
            errors += 1

    #-------------------------------------------------

    LoS = ['/* comment runs on beyond file ...', '....']
    err = preprocess_list_of_strings(LoS)
    if err != ParserError.UNTERMINATED_COMMENT :
        print "Expected ParserError.UNTERMINATED_COMMENT (errnum %d) but saw %d." % \
            ( ParserError.UNTERMINATED_COMMENT, err)
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
