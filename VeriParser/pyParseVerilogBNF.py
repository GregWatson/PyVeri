# Pyparsing BNF definition for verilog

from pyparsing import *

def f(t):
    print t

def new_Verilog_EBNF_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, SEMICOLON, COLON = map(Suppress, '()[];:')

    simple_Identifier = Word(alphas+"_", alphanums+"_$")

    const_expr = Word(nums) #fixme - can be more complex than this

    list_of_ports = LPAREN + Group(delimitedList(simple_Identifier)) + RPAREN

    _range  = LBRACK + Group(const_expr + COLON + const_expr) + RBRACK # msb:lsb

    reg_identifier = Group(simple_Identifier)

    reg_or_mem_identifier = reg_identifier   #fixme : or memory identifier 

    list_of_reg_identifiers = Group(delimitedList(reg_or_mem_identifier)) 

    reg_declaration = Suppress('reg') + Group( Optional(Literal('signed')) \
                                             + Optional(_range)            \
                                             + list_of_reg_identifiers )   \
                      + SEMICOLON

    module_item_declaration = reg_declaration # fixme - lots more to go

    module_item  = module_item_declaration    # fixme - lots more to go

    module_item_list = Group(OneOrMore(module_item))

    module_decl = Group( \
                    Suppress(Literal('module')) + simple_Identifier   \
                  + Optional(list_of_ports)     + SEMICOLON           \
                  + Optional(module_item_list)                        \
                  + Suppress(Literal('endmodule')) )


    parser = module_decl

    # actions
    module_item_list.setParseAction       ( lambda t: t[0].insert(0,'module_item_list'))
    module_decl.setParseAction            ( lambda t: t[0].insert(0,'module_decl'))
    list_of_ports.setParseAction          ( lambda t: t[0].insert(0,'list_of_ports'))
    _range.setParseAction                 ( lambda t: t[0].insert(0,'range'))
    list_of_reg_identifiers.setParseAction( lambda t: t[0].insert(0,'list_of_reg_identifiers'))
    reg_identifier.setParseAction         ( lambda t: t[0].insert(0,'reg_identifier'))
    reg_declaration.setParseAction        ( lambda t: t[0].insert(0,'reg_declaration'))
    return parser




####################################################
if __name__ == '__main__' :

    import VeriModule

    def printL(L, indent=''):
        if type(L) is list:
            print "list!"
            print "%s[" % indent
            for l in L: printL(l, indent+'   ')
            print "%s]" % indent
        else:
            print "%s%s" % (indent, L)
        


    data = """
module my_module ( port1, port2 ); reg [31:0] r1, r2; endmodule

    """    

    parser = new_Verilog_EBNF_parser()
    parsed_data = parser.parseString(data, True)

    for el in parsed_data:
        print el
    if parsed_data:
        m1 = VeriModule.VeriModule(parsed_data)
        print m1.to_string()
    else:
        print "No module_decl in text."

# EBNF from http://www.externsoft.ch/download/verilog.html
