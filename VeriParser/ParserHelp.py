##################################################
#
# ParserHelp - helper functions
#
##################################################

import ParserError

simpleID_firstChar   = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
simpleID_restOfChars = simpleID_firstChar + '0123456789$'

def get_simple_identifier_at_offset( line, offset ):
    ''' Expect a simple identifier in line starting at offset.
        Return (err, name of identifier)
    '''
    l = len(line)
    if offset >= l: return (-1,'')
    if not line[offset] in simpleID_firstChar:  return (-1,'')
    end_pos = offset+1
    while end_pos < l:
        if not line[end_pos] in simpleID_restOfChars: return(0,line[offset:end_pos])
        end_pos += 1
    return(0,line[offset:end_pos])


def find_first_simple_id_substr(text, sub, offset):
    ''' Find earliest occurrence of simple_ID sub in text starting from start.
        The simple_ID must be a complete word - not a substring.
        So looking for sub x in 'xx x' should return 3 not 0.
        return position where sub starts, else -1
    '''
    if not len(text) or not len(sub): return -1
    start = offset
    while start < len(text):
        pos = text.find(sub, start)
        if pos == -1: return -1
        start = pos + 1  # ready to keep looking if pos doesnt work out.

        # if previous char is legal in simple_ID then this is not a match
        if pos > 0 and ( text[pos-1] in simpleID_restOfChars ) : continue

        # if char after sub is legal in simple_ID then this is not a match
        nxt = pos + len(sub)
        if nxt < len(text) and ( text[nxt] in simpleID_restOfChars ) : continue

        return pos

    return -1

##################################################
#
# balanced string functions.
#
# A balanced string is one that starts with an open pair 
# char such as ( or { or [ and which then ends with
# the apropriate closing pair char: )}]. But the functions
# allow the use of other pair chars inside, and only finish
# when the contents are balanced or there is no text left (err).
#
# 
##################################################

_opening_pair_chars = r'([{'
_closing_pair_chars = r')]}'
_closing_pair_char_of = { '(':')', '[':']', '{':'}' }

def get_comma_sep_exprs_from_balanced_string(line, nxt_pos, debug=0):
    ''' Given balanced string starting at line[nxt_pos], then try to parse
        line as a comma separated sequence of expressions. 
        First char of string must be an opening pair char.
        Return (err, close_pos, list of exprs)
        where err is non-zero for error
              close_pos is position in string of closing pair char
              list of exprs is just that.
    '''
    l = len(line)
    if nxt_pos >= l: 
        print "Internal ERROR:get_comma_sep_exprs_from_balanced_string: next_pos arg outside string."
        return ( ParserError.SE_SYNTAX_ERROR, 0, [] )
    if line[nxt_pos] not in _opening_pair_chars: 
        print "Internal ERROR:get_comma_sep_exprs_from_balanced_string: start char is not in", _opening_pair_chars
        return ( ParserError.SE_SYNTAX_ERROR, 0, [] )

    stack      = [ line[nxt_pos] ]
    pos        = nxt_pos+1
    expr_start = nxt_pos+1
    exprL      = []
    delim      = ','

    while pos < l :

        c = line[pos]

        if c in _closing_pair_chars:
            if c == _closing_pair_char_of[stack[-1]]:
                stack.pop()
                if debug: print "DBG: saw",c,"stack is now", stack
                if not stack: 
                    exprL.append( line[expr_start:pos].strip() )
                    return (0, pos, exprL)
            else: # unbalanced pair - err
                if c == ')': return ( ParserError.SE_UNBALANCED_CLOSING_PAREN, 0, [] )
                if c == ']': return ( ParserError.SE_UNBALANCED_CLOSING_BRKT , 0, [] )
                if c == '}': return ( ParserError.SE_UNBALANCED_CLOSING_BRACE, 0, [] )
                return( ParserError.SE_SYNTAX_ERROR, 0, [] )
        else:
            if c in _opening_pair_chars:
                stack.append(c)
                if debug: print "DBG: saw",c,"stack is now", stack
            else:
                if c == delim:  # only have expr if stack len is 1. 
                    if len(stack) == 1:
                        exprL.append( line[expr_start:pos].strip() )
                        if debug: print "DBG: exprL is now", exprL
                        expr_start = pos+1

        pos += 1            

    return (ParserError.SE_NO_CLOSING_PAREN, 0, [] )

