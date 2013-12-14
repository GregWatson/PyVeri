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
        self.text = []                # actual src text. May be modified
        self.status = SourceText.NONE
        self.original_line_num  = []  # line num in original file
        self.original_file_idx  = []  # index of src filename for each line.
        self.original_file_list = [] 
        

    def load_source_from_file(self, filename):

        return self.load_source_from_file_to_line(filename, 0)

    def load_source_from_file_to_line(self, filename, offset):
        ''' Load new src file into self.text. Place first line of
            the src at location 'offset' in array text (shift
            everything else down) and renumber original_line_num
            accordingly.
        '''
        assert( offset <= len(self.text) )

        try:
            f = open(filename)
            new_text = map( lambda x: x.rstrip(), f.readlines())
            f.close()
        except IOError:
            return FILE_ERROR

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

        print new_text
        print new_line_num
        print new_file_num

        for ix in xrange(len(self.text)): 
            print "%s %3d : %s" % (self.original_file_list[self.original_file_idx[ix]], self.original_line_num[ix], self.text[ix])

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