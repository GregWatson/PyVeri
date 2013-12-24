# Pyparsing BNF definition for verilog

from pyparsing import *

def new_Verilog_EBNF_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK = map(Suppress, "()[]")

    simple_Identifier = Word(alphas+"_", alphanums+"_$")

    list_of_ports = LPAREN + Group(delimitedList(simple_Identifier)) + RPAREN

    module_item = Group(OneOrMore(Word(nums))) #fixme

    module_decl = Group( \
                    Suppress(Literal('module')) + simple_Identifier('module_name')   \
                  + Optional(list_of_ports('port_list')) + Suppress(';')             \
                  + module_item('module_item_list') + Suppress(Literal('endmodule')) )

    parser = module_decl

    return parser



####################################################
if __name__ == '__main__' :

    data = """
module my_module ( port1, port2 ); 1 2 3 endmodule

    """    

    parser = new_Verilog_EBNF_parser()
    parseL = parser.parseString(data, True)
    print parseL
    for item in parseL : 
        print item, `item`

# EBNF from http://www.externsoft.ch/download/verilog.html
