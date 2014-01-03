# Verilog Macros

import re
import ParserError
import ParserHelp

class VMacro(object):

    # macro name is simple identifier: [ a-zA-Z_ ] { [ a-zA-Z0-9_$ ] 

    pat_macro_blank          = re.compile(r'\s* ( [a-zA-Z_][\w_\$]+ ) \s* $', re.X)
    pat_macro_without_params = re.compile(r'\s* ( [a-zA-Z_][\w_\$]+ ) \s+ (.*)', re.X)
    pat_macro_with_params    = re.compile(r'\s* ( [^\s(]+ ) \( ( [^)]+ ) \) \s+ (.*)', re.X)

    def __init__(self, macro_defn, line_num=0, filename='unspecified'):
        ''' macro_defn = full text of macro such as 'my_macro(x,y) (x + y )'
            Note: `define has already been stripped.
        '''

        self.name     = ''
        self.argList  = []
        self.text     = ''         # body of the macro
        self.line_num = line_num
        self.filename = filename

        # blank macro;  `define fred
        match = VMacro.pat_macro_blank.match(macro_defn)

        if match:
            self.name    = match.group(1)
            return

        #macro with args: `define my_macro(x,y) (x + y )
        match = VMacro.pat_macro_with_params.match(macro_defn)

        if match:
            self.name    = match.group(1)
            args         = match.group(2)
            self.text    = match.group(3)

            args = args.strip()
            self.argList = map ( lambda x: x.strip(), args.split(',') )
         
            return

        # macro without args: `define my_simple_macro vector[10:0]
        match = VMacro.pat_macro_without_params.match(macro_defn)

        if match:
            self.name = match.group(1)
            self.text = match.group(2)
            return

        ParserError.report_syntax_err( ParserError.SE_BAD_MACRO_DEFN, line_num, filename)

    
    def subst_args_in_body(self, argL):
        ''' replace formal params in self.text with params provided in argL.
            Return (err, modified body (string))
        '''
        if len(argL) != len(self.argList): 
            return (ParserError.SE_MACRO_HAS_WRONG_NUMBER_PARAMS, '')

        body = self.text
        if not len(argL) or not len(body): return (0,body)


        # replace occurrences of formal by actual
        start = 0   # where in body we can start looking for a formal
        while start < len(body):

            # find earliest occurrence of any formal in body.
            formal_start = -1
            for (formal_ix, actual_ix) in zip( self.argList, argL):

                pos_ix = ParserHelp.find_first_simple_id_substr( body, formal_ix, start )

                if pos_ix != -1 and ( formal_start == -1 or pos_ix < formal_start ):
                    (formal_start, formal, actual) = (pos_ix, formal_ix, actual_ix)

            if formal_start == -1: return (0, body)

            # yes, it's an instance of the formal param.
            body  = body[0:formal_start] + actual + body[formal_start+len(formal):]
            start = formal_start + len(actual)

        return (0, body)



    def __str__(self):
        if not len(self.argList):
            return "MACRO from line %d file \"%s\" : %s '%s'" % \
                (self.line_num, self.filename, self.name, self.text)
        return "MACRO from line %d file \"%s\" : %s( %s ) '%s'" % \
            (self.line_num, self.filename, self.name,           \
             ','.join(self.argList), self.text)
