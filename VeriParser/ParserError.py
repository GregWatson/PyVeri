###################################################
#
# ParserError codes
#
###################################################

import sys

e = []

NO_ERROR                 = 0 ; e.append( 'NO_ERROR' )
ERR_UNTERMINATED_COMMENT = 1 ; e.append( 'ERR_UNTERMINATED_COMMENT')
ERR_FILE_I_O             = 2 ; e.append( 'ERR_FILE_I_O')
ERR_UNTERMINATED_MACRO   = 3 ; e.append( 'ERR_UNTERMINATED_MACRO')
BAD_MACRO_DEFN           = 4 ; e.append( 'BAD_MACRO_DEFN')

def report_syntax_err(errnum, line_num, filename):
    print "ERROR: Syntax error %s in file \"%s\" at line %d." % (e[errnum], filename, line_num)
    sys.exit(1)
