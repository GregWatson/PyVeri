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
        self.original_file_num  = []  # index of src filename for each line.
        self.original_file_list = [] 
        

    def load_source_from_file(self, filename):

        self.load_source_from_file_to_line(filename, 0)

    def load_source_from_file_to_line(self, filename, offset):
        ''' Load new src file into self.text. Place first line of
            the src at location 'offset' in array text (shift
            everything else down) and renumber original_line_num
            accordingly.
        '''
        assert( offset <= len(self.text) )

        try:
            f = open(filename)
            l_text = map( lambda x: x.rstrip(), f.readlines())
            f.close()
        except IOError:
            return FILE_ERROR











####################################################
if __name__ == '__main__' :

    f = "../Tests/data/simple1.v"
    obj = SourceText();
    if obj.load_source_from_file(f) :
        print "File error when opening %s" % f
        sys.exit(1)
