# Top level compiler code.
# Given a parse tree, compile it.

import Global, VeriModule, VeriTime
import sys


class Compiler(object):

    def __init__(self):

        self.module_parse_tree = {}  # dict maping module name to modules parse tree.
        self.timescale         = VeriTime.TimeScale() # current timescale


    def compile_parse_tree(self, gbl, parse_tree):
        ''' Given a global object and a parse_tree (created by PyParsing)
            compile the parse tree and update the global object as needed.
            After compilation gbl should contain the initial event list
            and the database of all signals.
        '''

        for el in parse_tree:
            # print "<", el, ">"
            if el[0] == 'module_decl':
                m = VeriModule.VeriModule( self.timescale)
                m.process_element(gbl, 0, el)
                if gbl.debug:
                    print m
                    print "module scope is ",m.scope
                    print gbl
                continue
            if el[0] == 'timescale':
                self.timescale.process_timescale_spec(scaleL = el[1], precL = el[2])
                if gbl.debug: print "timescale=",str(self.timescale)
            else:
                print "Dont know how to process",el

