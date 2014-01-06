######################################################
# SourceText.py
#
# Class to hold source text and associated structures.
######################################################

import ParserError

class SourceText(object):

    NONE         = 0
    SRC_LOADED   = 1
    PREPROCESSED = 2

    def __init__(self):
        self.text = []                # actual src text. May be modified. no CR
        self.status = SourceText.NONE
        self.original_line_num  = []  # line num in original file
        self.original_file_idx  = []  # index of src filename for each line.
        self.original_file_list = [] 
        self.debug  = 0
        self.macros = {}  # dict of VMacro objects indexed by macro name.


    def print_text(self):  
        ''' Print self.text and assoc info'''
        assert len(self.text) == len(self.original_line_num)
        assert len(self.text) == len(self.original_file_idx)

        for ix,l in enumerate(self.text):
            print "%3d [%3d %s]  '%s'" % ( ix, self.original_line_num[ix], \
                                           self.original_file_list[self.original_file_idx[ix]], \
                                           l )

    def delete_text_range(self, first, last=-1 ):
        ''' Remove the text located at indices first through last inclusive.
            Also fix other data associated with those lines.
        '''
        if last == -1: last = first
        assert ( len(self.text) > last )
        assert ( last >= first )
        ix = last;
        while ix >= first:
            del self.text[ix]
            del self.original_line_num[ix]
            del self.original_file_idx[ix]
            ix = ix - 1


    @staticmethod
    def get_text_list_from_string_and_strip_CR(string):
        ''' get lines of text from single string which has 
            internal CR to separate lines.
        '''
        textL = string.split('\n')
        textL[:] = [ x.rstrip() for x in textL ] # in-place list modification
        return textL  



    @staticmethod
    def load_text_from_file_and_strip_CR(filename):
        ''' Load text from file, stripping CR. 
            Return (err-code, list of strings).
        '''
        try:
            t = open(filename).read()
            new_text = SourceText.get_text_list_from_string_and_strip_CR(t)
        except IOError:
            return (ParserError.ERR_FILE_I_O,[])

        return (0,new_text)


    def load_source_from_file(self, filename):

        return self.load_source_from_file_to_line(filename, 0)

    def load_source_from_string(self, string):

        textL = SourceText.get_text_list_from_string_and_strip_CR(string)
        return self.insert_source_from_string_array_to_line( textL, 'text_string', 0)


    def load_source_from_file_to_line(self, filename, offset):
        ''' Load new src file into self.text. Place first line of
            the src at location 'offset' in array text (shift
            everything else down) and renumber original_line_num
            accordingly.
        '''
        assert( offset <= len(self.text) )

        (err, new_text) = self.load_text_from_file_and_strip_CR(filename)
        if err: return err

        return self.insert_source_from_string_array_to_line(new_text, filename, offset)


    def insert_source_from_string_array_to_line(self, new_text, filename, offset):
        ''' Insert the given new_text into the self.text array
            at specified offset within self.text. Associate the new text
            as coming from filename.
            Note: offset is index in array self.text, not line number in text.
            Return err or 0
        '''

        # create line num and filename mappings for the new lines.
        new_line_num = [ a+1 for a in range( len(new_text) ) ]

        if filename in self.original_file_list:
            f_index = self.original_file_list.index(filename)
        else:
            f_index = len(self.original_file_list)
            self.original_file_list.append(filename)
        
        new_file_num = [ f_index for a in range( len(new_text) ) ] 
        
        self.text             [offset:offset] = new_text
        self.original_line_num[offset:offset] = new_line_num
        self.original_file_idx[offset:offset] = new_file_num

        return 0






####################################################
if __name__ == '__main__' :

    f = "../Tests/data/simple1.v"
    obj = SourceText();
    if obj.load_source_from_file(f) :
        print "File error when opening %s" % f
        sys.exit(1)

    if obj.load_source_from_file_to_line(f, 5) :
        print "File error when opening %s" % f
        sys.exit(1)

