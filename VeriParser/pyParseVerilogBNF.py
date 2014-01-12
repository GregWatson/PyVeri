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

    simple_Identifier = Word(alphas+"_", alphanums+"_.$")

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
    expression = Group(Word(nums)) # fixme

    blocking_assignment = Group( reg_lvalue + Suppress('=')         \
                                 + Optional(delay_or_event_control) \
                                 + expression )

    blocking_assignment_semi = blocking_assignment + SEMICOLON

    statement << Group( seq_block | blocking_assignment_semi ) # fixme - lots more to go

    initial_construct = Suppress('initial') + statement

    always_construct = Suppress('always') + statement

    module_item_declaration = reg_declaration # fixme - lots more to go

    module_item  = module_item_declaration                         \
                   | initial_construct                             \
                   | always_construct  # fixme - lots more to go

    module_item_list = Group(OneOrMore(module_item))

    module_name = Group(simple_Identifier)

    module_decl = Group( \
                    Suppress(Literal('module')) + module_name   \
                  + Optional(list_of_ports)     + SEMICOLON     \
                  + Optional(module_item_list)                  \
                  + Suppress(Literal('endmodule')) )

    # ---- timescale
    time_1_10_100 = Literal('100') | Literal('10') | Literal('1')
    time_unit_string = Literal('s')  | Literal('ms') | Literal('us') |   \
                       Literal('ns') | Literal('ps') | Literal('fs')
    time_unit = Group( time_1_10_100 + time_unit_string )
    timescale = Group( Suppress(r'`timescale') + time_unit + Suppress('/') + time_unit )

    source = timescale | module_decl

    parser = OneOrMore(source)

    # actions
    
    always_construct.setParseAction       ( lambda t: t[0].insert(0,'always'))
    blocking_assignment.setParseAction    ( lambda t: t[0].insert(0,'blocking_assignment'))
    block_identifier.setParseAction       (  f_name_identifier('block_identifier'))
    block_id_and_opt_decl.setParseAction  ( lambda t: t[0].insert(0,'block_id_and_opt_decl'))
    expression.setParseAction             ( lambda t: t[0].insert(0,'expression'))
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
    timescale.setParseAction              ( lambda t: t[0].insert(0,'timescale'))
    return parser




####################################################
if __name__ == '__main__' :
    pass

# EBNF from http://www.externsoft.ch/download/verilog.html

# Greg:
# Handle delayed statement.  e.g. #10 r = 1
#   - this needs concept of current timescale.  (relative to fs?)
#   - so process `timescale commands?

# handle signal dependency: if r changes then b changes ( e.g. if wire b = r + 1 )

# handle module instantiation - amke sure signals at both module levels are handled
# correctly if they are passed between the modules.
