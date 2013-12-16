# Verilog Macros

import re
import ParserError

class VMacro(object):

    # macro name is simple identifier: [ a-zA-Z_ ] { [ a-zA-Z0-9_$ ] 

    pat_macro_blank          = re.compile(r'\s* ( [a-zA-Z_][\w_\$]+ ) \s* $', re.X)
    pat_macro_without_params = re.compile(r'\s* ( [a-zA-Z_][\w_\$]+ ) \s+ (.*)', re.X)
    pat_macro_with_params    = re.compile(r'\s* ( [^\s(]+ ) \( ( [^)]+ ) \) \s+ (.*)', re.X)

    def __init__(self, macro_text, line_num=0, filename='unspecified'):
        ''' macro_text = full text of macro such as 'my_macro(x,y) (x + y )'
            Note: `define has already been stripped.
        '''

        self.name     = ''
        self.argList  = []
        self.text     = ''
        self.line_num = line_num
        self.filename = filename

        # blank macro;  `define fred
        match = VMacro.pat_macro_blank.match(macro_text)

        if match:
            self.name    = match.group(1)
            return

        #macro with args: `define my_macro(x,y) (x + y )
        match = VMacro.pat_macro_with_params.match(macro_text)

        if match:
            self.name    = match.group(1)
            args         = match.group(2)
            self.text    = match.group(3)

            args = args.strip()
            self.argList = map ( lambda x: x.strip(), args.split(',') )
         
            return

        # macro without args: `define my_simple_macro vector[10:0]
        match = VMacro.pat_macro_without_params.match(macro_text)

        if match:
            self.name = match.group(1)
            self.text = match.group(2)
            return

        ParserError.report_syntax_err( ParserError.SE_BAD_MACRO_DEFN, line_num, filename)

    def __str__(self):
        if not len(self.argList):
            return "MACRO from line %d file \"%s\" : %s '%s'" % \
                (self.line_num, self.filename, self.name, self.text)
        return "MACRO from line %d file \"%s\" : %s( %s ) '%s'" % \
            (self.line_num, self.filename, self.name,           \
             ','.join(self.argList), self.text)
            
