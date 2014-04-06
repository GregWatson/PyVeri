# Top level compiler code.
# Given a parse tree, compile it.

import Global, VeriModule, VeriTime
import sys, copy
from PreProcess import *
from pyParseVerilogBNF import *

class Compiler(object):

    def __init__(self, gbl):

        self.module_parse_tree = {}  # dict mapping module name to that module's parse tree.
        self.timescale         = VeriTime.TimeScale() # current timescale
        self.gbl               = gbl

        #register compiler with the global object
        gbl.set_compiler(self)


    def compile_parse_tree(self, parse_tree, hier='', top_module=''):
        ''' Given a global object and a parse_tree (created by PyParsing)
            compile the parse tree and update the global object as needed.
            After compilation gbl should contain the initial event list
            and the database of all signals.
            gbl: global object
            parse_tree: from PyParsing
            hier: string indicating current module hierarchy.
            top_module: string. Name of top level module. else ''
        '''

        for el in parse_tree:
            # print "<", el, ">"

            if el[0] == 'module_decl':
                
                # Copy the parse tree and associate it with the module name 
                # in case we instantiate this module more than once.
                assert el[1][0] == 'module_name'
                mod_name = el[1][1]
                self.module_parse_tree[mod_name] = el.copy()

                # If top_module is set, and it's not this module, then don't compile it.
                if top_module and (mod_name != top_module): next

                m = VeriModule.VeriModule( self.timescale, hier=hier)
                m.process_element(self.gbl, 0, el)

                # global needs to track the top level module
                if ( not top_module or ( mod_name == top_module) ): self.gbl.set_top_module(m)

                if self.gbl.debug:
                    print m
                    print "module scope is ",m.scope
                    print self.gbl
                continue
            if el[0] == 'timescale':
                self.timescale.process_timescale_spec(scaleL = el[1], precL = el[2])
                if self.gbl.debug: print "timescale=",str(self.timescale)
            else:
                print "Dont know how to process",el



    ## Copy the ParseResult object associated with module 'mod_name'
    # @param self : Global object
    # @param mod_name : string. Name of the module to copy.
    # @return new ParseResult object or issues Error if not found
    def copy_parse_object_for_module(self, mod_name):
        if not mod_name in self.module_parse_tree:
            self.error("copy_parse_object_for_module: Module '%s' not found." % mod_name)
        return self.module_parse_tree[mod_name].copy()



    ## Error handling routine.
    # @param self : object
    # @param *args : list of strings to be printed in the error message.
    # @return : None  ( executes sys.exit(1) )
    def error(self, *args):
        print "ERROR: VeriCompile:",
        for arg in args: print arg,
        print
        sys.exit(1)








## Compile a verilog program given as a single string.
# @param program : string. The verilog program
# @param debug : debug vector integer
# @param opt_vec : options vector integer
# @param sim_end_time_fs : integer. Sim end time in fs
# @param top_module : string. Name of top level module. (or '')
# @return gbl object or None if error
def compile_string_as_string(program, debug=0, opt_vec=0, sim_end_time_fs=100000,top_module=''):
    ''' This is a helper function '''

    preProcess = PreProcess();
    preProcess.load_source_from_string(program)
    preProcess.preprocess_text()  # comments and includes and defines and undefs

    if debug: preProcess.print_text() 

    data = ''.join(preProcess.text)
    parser = new_Verilog_EBNF_parser()
    try:
        parsed_data = parser.parseString(data, True)

    except ParseException, err:
        print "err.line is ",err.line
        print "col is ", err.column
        text_lines = err.line.split(';')
        line_num = 0
        char_count = 0
        last_line  = None
        print_next_line  = False
        for line in text_lines:
            line += ';'
            line_num += 1
            if print_next_line:
                print "[%3d] %s" % (line_num, line)
                break    
            if ( char_count + len(line) ) >= err.column:
                if last_line: print "[%3d] %s" % (line_num-1, last_line)
                print "[%3d] %s" % (line_num, line)
                print "      " + " "*(err.column-char_count-1) + "^"
                print_next_line  = True
            else: 
                last_line = line
                char_count +=  len(line)

        print err
        return None

    # need Global gbl for tracking all signals and events
    gbl = Global.Global( sim_end_time_fs = sim_end_time_fs, 
                                   debug = debug )  


    # Compile the parse tree

    compiler = Compiler( gbl )
    compiler.compile_parse_tree( parsed_data, top_module=top_module )

    return gbl




