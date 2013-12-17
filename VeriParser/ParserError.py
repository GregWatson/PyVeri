###################################################
#
# ParserError codes
#
###################################################

import sys

e = []

NO_ERROR                         = 0  ; e.append( 'NO_ERROR' )
ERR_UNTERMINATED_COMMENT         = 1  ; e.append( 'ERR_UNTERMINATED_COMMENT')
ERR_FILE_I_O                     = 2  ; e.append( 'ERR_FILE_I_O')
ERR_UNTERMINATED_MACRO           = 3  ; e.append( 'ERR_UNTERMINATED_MACRO')
SE_BAD_MACRO_DEFN                = 4  ; e.append( 'BAD_MACRO_DEFN')
SE_ID_EXPECTED_AFTER_TICK        = 5  ; e.append( 'SE_ID_EXPECTED_AFTER_TICK')
SE_MACRO_NOT_DEFINED             = 6  ; e.append( 'SE_MACRO_NOT_DEFINED')
SE_SYNTAX_ERROR                  = 7  ; e.append( 'SE_SYNTAX_ERROR')
SE_UNBALANCED_CLOSING_PAREN      = 8  ; e.append( 'SE_UNBALANCED_CLOSING_PAREN')
SE_UNBALANCED_CLOSING_BRACE      = 9  ; e.append( 'SE_UNBALANCED_CLOSING_BRACE')
SE_UNBALANCED_CLOSING_BRKT       = 10 ; e.append( 'SE_UNBALANCED_CLOSING_BRKT')
SE_NO_CLOSING_PAREN              = 11 ; e.append( 'SE_NO_CLOSING_PAREN')
SE_MACRO_HAS_WRONG_NUMBER_PARAMS = 12 ; e.append( 'SE_MACRO_HAS_WRONG_NUMBER_PARAMS')

def report_syntax_err(errnum, line_num, filename):
    print "ERROR: Syntax error %s in file \"%s\" at line %d." % (e[errnum], filename, line_num)
    sys.exit(1)
