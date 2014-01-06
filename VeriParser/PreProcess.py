##################################################
#
# PreProcess - class to perform preprcoessing on a raw source file
#
##################################################

import ParserError, re
from SourceText import SourceText
from VMacro import VMacro
from ParserHelp import *

import sys

''' Preprocess a source verilog file:

    - strip comments but preserve lines.
    - process `include "filename" commands: insert file into text but 
      track line numbers back to original file.
    - process `define and corresponding use of a `define'd macro.
      (Note: macros may invoke other macros, and macros can have params)
    - process `undef to undefine a macro (remove it from table of known macros)

    See detailed comments at end of file.
'''

class PreProcess(SourceText):

    def __init__(self):
        
        super(PreProcess, self).__init__();
        self.text = [] # list of source text, no CR at EOL

    def preprocess_text(self):
        ''' Preprocess self.text. Return error if one occurs, else 0.
        '''
        err_code = self.strip_comments(self.text)
        if (err_code): return err_code
        err_code = self.preprocess_include_and_define()
        if (err_code): return err_code
        return 0

    @staticmethod       
    def strip_comments(text):
        '''
        text: List of verilog text
              Text lines must not end in CR (should have been stripped).
        Output: error code (0=ok)
        Effect: text is modified in-place.
        '''
        NONE = 0
        IN_LONG = 1

        state = NONE

        for line_num, line in enumerate(text):
            start = 0

            while ( start < len(line) ) :
                if state == NONE:
                    # Look for either // or /*
                    sc_ix = line.find('//',start)   # short comment location
                    lc_ix = line.find('/*',start)   # long comment location
                    # If we have neither then we are done for this line.
                    if ( sc_ix == -1 and lc_ix == -1 ) : 
                        text[line_num] = line
                        break
                    s_ix  = line.find('"',start)   # double quote that starts a string.

                    # see which comes first
                    sc_first = ( sc_ix >= 0 ) and                                \
                               ( ( s_ix == -1    or ( s_ix > sc_ix ) ) and
                                 ( lc_ix == -1 ) or ( lc_ix > sc_ix ) )
                    if sc_first:
                        line = line[0:sc_ix]
                        text[line_num] = line
                        break

                    # now check string ("....")
                    string_first = ( s_ix >= 0 ) and                            \
                                      ( lc_ix == -1 or ( lc_ix > s_ix ) )
                    if string_first:
                        # string starts before any comment. Advance to next " 
                        s_ix = line.find('"',s_ix+1)
                        if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                            text[line_num] = line
                            break
                        # if char before " is \ then the " doesnt count (it's \")
                        while s_ix != -1 and line[s_ix - 1] == '\\' :
                            s_ix = line.find('"',s_ix+1)
                        if ( s_ix == - 1 ) : # no closing " - error in verilog. ignore it here.
                            text[line_num] = line
                            break
                        start = s_ix + 1
                        if (start >= len(line) ) :
                            text[line_num] = line
                            break
                        continue

                    # Must be a long comment.
                    # If the long comment ends this line then we strip it out
                    # and go round again.
                    e_ix = line.find('*/',lc_ix+2)
                    if e_ix >= 0:
                        line = line[0:lc_ix] + line[e_ix+2:]
                        start = lc_ix
                        if ( start >= len(line) ):
                            text[line_num] = line
                            break
                    else: # didnt see end of comment - must run on.
                        line = line[0:lc_ix]
                        text[line_num] = line
                        state = IN_LONG
                        break

                else: # state is IN_LONG - look for first */ that ends the comment.
                    lc_ix = line.find('*/')
                    if lc_ix == -1 : # did not see */ in this line - comment continuing
                        text[line_num] = ''
                        break
                    # found */
                    line = line[lc_ix+2:]
                    if len(line) == 0:
                        text[line_num] = ''
                    state = NONE

        if state == IN_LONG:
            return ParserError.ERR_UNTERMINATED_COMMENT
        else:
            return 0

    def add_macro(self, macro_text, line_num, filename):
        ''' macro_text is a text string defined in filename at line line_num.
            Create macro object and add it to list of known macros. 
            Do not interpolate any `macro used in the definition - they are 
            interpolated when macro is used.
        '''
        macro = VMacro(macro_text, line_num, filename)
        if macro.name in self.macros:
            orig_macro = self.macros[macro.name]
            print "WARNING: redefined macro '%s' in file %s at line %d." \
                % (macro.name, macro.filename, macro.line_num)
            print "         Prev defined in file %s at line %d." \
                % (orig_macro.filename, orig_macro.line_num)
        
        self.macros[macro.name] = macro
        if self.debug: print "Added macro:", macro


    def undef_macro(self, macro_name, line_num, filename):
        ''' undef the specified macro name '''
        if macro_name not in self.macros:
            print "WARNING: Macro not previously defined: `undef macro '%s' in file %s at line %d." \
                % (macro_name, filename, line_num)
            return
        if self.debug: print "Undef'd Macro '%s' in file %s at line %d." \
                % (macro_name, filename, line_num)
        del self.macros[macro_name]


    def do_macro_substitution(self, line, line_num, filename):
        ''' Do a single macro substitution (if any).
            Note: assumes that first backtick is a macro subst - i.e.
                if it was a `include or something else then you better
                have dealt with it already.
            Returns modified line.
        '''
        tick_pos = line.find('`')
        if tick_pos == -1: return line
        # get macro name (after the tick)
        (err, macro_name) = get_simple_identifier_at_offset(line, tick_pos+1)
        if err:
            ParserError.report_syntax_err(ParserError.SE_ID_EXPECTED_AFTER_TICK, line_num, filename)
        if macro_name not in self.macros:
            ParserError.report_syntax_err(ParserError.SE_MACRO_NOT_DEFINED, line_num, filename)

        # Must differentiate between macro with args and without.
        # A macro with args must be followed by '(' immediately after name.

        nxt_pos = tick_pos + len(macro_name) + 1

        if nxt_pos >= len(line) or line[nxt_pos] != '(':  # simple macro (no args)

            line = line[0:tick_pos] + self.macros[macro_name].text + line[nxt_pos:]

        else: # macro with args

            (err, arg_end_pos, argL) = get_comma_sep_exprs_from_balanced_string(line, nxt_pos)
            if err:
                ParserError.report_syntax_err(err, line_num, filename)

            macro = self.macros[macro_name]

            # get the original macro body, replacing formal params with actual args.

            (err,new_body) = macro.subst_args_in_body(argL)
            if err: ParserError.report_syntax_err(err, line_num, filename)

            line = line[0:tick_pos] + new_body + line[arg_end_pos+1:]

        return line


    def insert_include_file(self, inc_file, index):
        ''' insert the specified `include file in self.text at the
            location specified by index. 
            Remove the old line (the `include line)
            Return err or 0
        '''
        if (self.debug): print "DBG: Including `include file '%s'" % inc_file
        (err, new_text) = self.load_text_from_file_and_strip_CR(inc_file)
        if err: return err

        err = self.strip_comments(new_text)
        if not err:  # replace this line with new text into self.text
            err = self.insert_source_from_string_array_to_line(new_text, inc_file, index)
        if err: return err
        self.delete_text_range( first=index+len(new_text)  )

        if (self.debug): 
            print "DBG: after including file",inc_file,"text is now:"
            self.print_text()   

        return 0


    def preprocess_include_and_define(self):
        ''' self.text already stripped of comments.
            Process `include lines as well as `define macros.
            Process macro instantiations (replace them with their definitions).
            Process `undef
            Modifies self.text in place.
            returns 0 or error_num
        '''
        pat_keywords = re.compile(r'(?:`timescale)')
        pat_include  = re.compile(r'`include\s*"([^"]+)"')
        pat_define   = re.compile(r'`define\s+(.+)')
        pat_undef    = re.compile(r'`undef\s+([a-zA-Z_][\w_$]*)')

        text_ix = 0

        while text_ix < len(self.text):

            line     = self.text[text_ix]
            line_num = self.original_line_num[text_ix]
            filename = self.original_file_list[self.original_file_idx[text_ix]]

            while line.find("`") != -1:

                # Ignore keywords
                match = pat_keywords.search(line)
                if match: # it's a keyword other than `include, `define etc.
                    break

                # Look for `include "filename". If found then read the text from that
                # file, strip comments, and insert it into self.text, replacing the
                # current `include line.

                match = pat_include.search(line)

                if match: # it's a `include.
                    inc_file = match.group(1)
                    err = self.insert_include_file( inc_file, text_ix )
                    if err: return err
                    line = self.text[text_ix]  # this line has changed. process it again

                else:
                    # Look for `define              
                    match = pat_define.search(line)

                    if match: # it's a `define, so add the macro
                        def_text     = [ match.group(1) ]

                        self.text[text_ix] = '' # remove text.
                        while def_text[-1].endswith('\\'):    # macro continues to next line
                            def_text[-1] = def_text[-1].rstrip('\\')
                            text_ix += 1
                            if text_ix >= len(self.text): return ParserError.ERR_UNTERMINATED_MACRO
                            def_text.append(self.text[text_ix])
                            self.text[text_ix] = '' # remove text.
                        macro = ''.join(def_text)
                        self.add_macro( macro, line_num, filename )
                        break

                    else:  # look for undef
                        match = pat_undef.search(line)

                        if match: # it's a `undef so delete the macro
                            macro_name = match.group(1)
                            self.undef_macro(macro_name, line_num, filename )
                            self.text[text_ix] = '' # remove text.
                            break

                        # Not a keyword, so check for macro substitution.
                        else:
                            self.text[text_ix] = self.do_macro_substitution(line, line_num, filename)    
                            line = self.text[text_ix]   # this line has changed. process it again

            text_ix +=1 

        return 0


'''
Remove all comments (long and short) but preserve resulting blank lines:

    Watch out for comment chars starting in strings - ignore them.
    Once in a long comment (/* ... */) we ignore everything until we see */
    Short comment ( // ) is to end of line.

'''
