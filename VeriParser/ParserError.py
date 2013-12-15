###################################################
#
# Parser Error codes
#
###################################################

import sys

NO_ERROR                 = 0
ERR_UNTERMINATED_COMMENT = 1
ERR_FILE_I_O             = 2
ERR_UNTERMINATED_MACRO   = 3
ERR_SYNTAX_ERR           = 4

def report_syntax_err(errnum, line_num, filename):
    print "Syntax error in file \"%s\" at line %d." % (filename, line_num)
    sys.exit(1)
