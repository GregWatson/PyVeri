# Verilog Macros

import re
import ParserError

class VMacro(object):

    pat_macro_without_params = re.compile(r'\s* ( [\w_]+ ) \s+ (.*)', re.X)
    pat_macro_with_params    = re.compile(r'\s* ( [^\s(]+ ) \( ( [^)]+ ) \) \s+ (.*)', re.X)

    def __init__(self, macro_text, line_num=0, filename='unspecified'):
        ''' macro_text = full text of macro such as 'my_macro(x,y) (x + y )'
        '''

        self.name     = ''
        self.argList  = []
        self.text     = ''
        self.line_num = line_num
        self.filename = filename

        match = VMacro.pat_macro_with_params.match(macro_text)

        if match:
            self.name    = match.group(1)
            args         = match.group(2)
            self.text    = match.group(3)

            args = args.strip()
            self.argList = map ( lambda x: x.strip(), args.split(',') )
         
            return

        match = VMacro.pat_macro_without_params.match(macro_text)

        if match:
            self.name = match.group(1)
            self.text = match.group(2)
            return

        ParserError.report_syntax_err( ParserError.BAD_MACRO_DEFN, line_num, filename)

    def __str__(self):
        return "MACRO from line %d file \"%s\" : %s( %s ) %s" % \
            (self.line_num, self.filename, self.name,           \
             ','.join(self.argList), self.text)
            
