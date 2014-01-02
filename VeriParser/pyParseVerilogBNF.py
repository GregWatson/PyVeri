# Pyparsing BNF definition for verilog
#
# Todo: error handling when running pyparsing.
#       - associate filename and linenumber with syntax objects.
#

from pyparsing import *

def f(t):
    print t

def f_name_identifier(name):
    def f(l):
        return [[name, l[0]]]
    return f

def new_Verilog_EBNF_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, SEMICOLON, COLON = map(Suppress, '()[];:')
    signed = Literal('signed')

    simple_Identifier = Word(alphas+"_", alphanums+"_$")

    const_expr = Word(nums) #fixme - can be more complex than this

    list_of_ports = LPAREN + Group(delimitedList(simple_Identifier)) + RPAREN

    _range  = LBRACK + Group(const_expr + COLON + const_expr) + RBRACK # msb:lsb

    reg_identifier   = simple_Identifier.copy()
    block_identifier = simple_Identifier.copy()

    reg_or_mem_identifier = reg_identifier   #fixme : or memory identifier 

    list_of_reg_identifiers = Group(delimitedList(reg_or_mem_identifier)) 

    statement = Forward()

    reg_declaration = Suppress('reg') + Group( Optional(signed)            \
                                             + Optional(_range)            \
                                             + list_of_reg_identifiers )   \
                      + SEMICOLON
    
    block_item_declaration = reg_declaration # fixme - lots more to go

    block_id_and_opt_decl = Group( COLON + block_identifier                     \
                                         + ZeroOrMore(block_item_declaration) )

    seq_block = Group( Suppress('begin')                                   \
                       + Optional(block_id_and_opt_decl)                   \
                       + ZeroOrMore(statement) + Suppress('end') )

    reg_lvalue = reg_identifier.copy() # fixme - lots more to go

    delay_or_event_control = Literal('#')  # fixme
    expression = Word(nums) # fixme

    blocking_assignment = Group( reg_lvalue + Suppress('=')         \
                                 + Optional(delay_or_event_control) \
                                 + expression )

    blocking_assignment_semi = blocking_assignment + SEMICOLON

    statement << Group( seq_block | blocking_assignment_semi ) # fixme - lots more to go

    initial_construct = Suppress('initial') + statement

    module_item_declaration = reg_declaration # fixme - lots more to go

    module_item  = module_item_declaration \
                   | initial_construct   # fixme - lots more to go

    module_item_list = Group(OneOrMore(module_item))

    module_name = Group(simple_Identifier)

    module_decl = Group( \
                    Suppress(Literal('module')) + module_name   \
                  + Optional(list_of_ports)     + SEMICOLON     \
                  + Optional(module_item_list)                  \
                  + Suppress(Literal('endmodule')) )


    parser = module_decl

    # actions
    
    blocking_assignment.setParseAction    ( lambda t: t[0].insert(0,'blocking_assignment'))
    block_identifier.setParseAction       (  f_name_identifier('block_identifier'))
    block_id_and_opt_decl.setParseAction  ( lambda t: t[0].insert(0,'block_id_and_opt_decl'))
    initial_construct.setParseAction      ( lambda t: t[0].insert(0,'initial'))
    list_of_ports.setParseAction          ( lambda t: t[0].insert(0,'list_of_ports'))
    list_of_reg_identifiers.setParseAction( lambda t: t[0].insert(0,'list_of_reg_identifiers'))
    module_item_list.setParseAction       ( lambda t: t[0].insert(0,'module_item_list'))
    module_decl.setParseAction            ( lambda t: t[0].insert(0,'module_decl'))
    module_name.setParseAction            ( lambda t: t[0].insert(0,'module_name'))
    _range.setParseAction                 ( lambda t: t[0].insert(0,'range'))
    reg_identifier.setParseAction         ( f_name_identifier('reg_identifier'))
    reg_lvalue.setParseAction             ( f_name_identifier('reg_lvalue'))
    reg_declaration.setParseAction        ( lambda t: t[0].insert(0,'reg_declaration'))
    seq_block.setParseAction              ( lambda t: t[0].insert(0,'seq_block'))
    signed.setParseAction                 ( lambda t: [t] )
    statement.setParseAction              ( lambda t: t[0].insert(0,'statement'))
    return parser




####################################################
if __name__ == '__main__' :

    import VeriModule, sys

    def printL(L, indent=''):
        if type(L) is list:
            print "list!"
            print "%s[" % indent
            for l in L: printL(l, indent+'   ')
            print "%s]" % indent
        else:
            print "%s%s" % (indent, L)
        


    data = """module my_module ( port1, port2) ; reg [31:0] r1, r2; endmodule """
    # data = """module my_module ( port1, port2) ; initial begin : block_id reg r; reg aaa; r = 1; aaa = 3; end endmodule """
    #data = """module my_module ( port1, port2) ; initial begin : block_id reg r; r = 1; aaa = 3; end endmodule """
    # data = """module my_module ( port1, port2) ; initial r = 1;endmodule """

    parser = new_Verilog_EBNF_parser()
    try:
        parsed_data = parser.parseString(data, True)
    except Exception as e:
        print `e`
        sys.exit(1)

    # construct sim structures from parse tree

    for el in parsed_data:
        if el[0] == 'module_decl':
            m = VeriModule.VeriModule()
            m.process_element(el)
            print m
            m.initialize()
            print m.scope
        else:
            print "Dont know how to process",el[0]

    # run sim



# EBNF from http://www.externsoft.ch/download/verilog.html



# Next: variables need to be defined within a nested scope.
#       Can we statically allocate all vars or do these need to be created
#       dynamically?
#       i.e. what would we do for something like:
#            for (i=1;i<1000;i=i+1) begin reg r; r = a ^ b; end
#
#
