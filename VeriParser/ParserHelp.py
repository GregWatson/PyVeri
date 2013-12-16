##################################################
#
# ParserHelp - helper functions
#
##################################################

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
