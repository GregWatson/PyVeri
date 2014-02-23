# Top level compiler code.
# Given a parse tree, compile it.

import Global, VeriModule, VeriTime
import sys, copy


class Compiler(object):

    def __init__(self):

        self.module_parse_tree = {}  # dict mapping module name to that module's parse tree.
        self.timescale         = VeriTime.TimeScale() # current timescale


    def compile_parse_tree(self, gbl, parse_tree):
        ''' Given a global object and a parse_tree (created by PyParsing)
            compile the parse tree and update the global object as needed.
            After compilation gbl should contain the initial event list
            and the database of all signals.
        '''

        for el in parse_tree:
            #print "<", el, ">"

            if el[0] == 'module_decl':
                
                # Copy the parse tree and associate it with the module name.
                assert el[1][0] == 'module_name'
                mod_name  = el[1][1]
                print "Compiler: found source definition for module", mod_name
                self.module_parse_tree[mod_name] = el.copy()

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

