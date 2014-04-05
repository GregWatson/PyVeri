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

    LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE, SEMICOLON, COLON = map(Suppress, '()[]{};:')
    signed = Literal('signed')
    ASSIGN = Literal('assign')

    simple_Identifier = Word(alphas+"_", alphanums+"_.$")

    signed_integer   = Word(nums+'-', nums)
    unsigned_integer = Word(nums)
    unsigned_number  = Word(nums, nums+'.') # float

    const_expr = Word(nums) #fixme - can be more complex than this

    statement = Forward()

    expression = Forward()

    list_of_ports = LPAREN + Group(delimitedList(simple_Identifier)) + RPAREN

    _range  = LBRACK + Group(const_expr + COLON + const_expr) + RBRACK # msb:lsb

    block_identifier  = simple_Identifier.copy()
    module_identifier = simple_Identifier.copy()
    net_identifier    = simple_Identifier.copy()
    param_identifier  = simple_Identifier.copy()
    port_identifier   = simple_Identifier.copy()
    reg_identifier    = simple_Identifier.copy()
    name_of_instance  = simple_Identifier.copy()

    reg_or_mem_identifier = reg_identifier   #fixme : or memory identifier 

    reg_identifier_expr  = Group ( reg_identifier + LBRACK + expression + RBRACK )
    reg_identifier_range = Group ( reg_identifier + _range)

    net_identifier_expr  = Group ( net_identifier + LBRACK + expression + RBRACK )
    net_identifier_range = Group ( net_identifier + _range)


    list_of_reg_identifiers = Group(delimitedList(reg_or_mem_identifier)) 
    list_of_net_identifiers = Group(delimitedList(net_identifier)) 

    delay_value = unsigned_number | param_identifier

    delay_control = Group( Suppress('#') + delay_value )

    monitor = Group(  Suppress('$monitor') + LPAREN 
                    + delimitedList(net_identifier) 
                    + RPAREN + SEMICOLON )


    reg_declaration = ( Suppress('reg') + Group( Optional(signed)            
                                               + Optional(_range)            
                                               + Optional(delay_control)
                                               + list_of_reg_identifiers )   
                        + SEMICOLON )
    
    net_declaration = ( Suppress('wire') + Group( Optional(signed)            
                                               +  Optional(_range)
                                               +  Optional(delay_control)
                                               +  list_of_net_identifiers )   #fixme : or list of net_decl_assignments
                        + SEMICOLON )

    input_declaration = ( Suppress('input') + Group(    Optional(_range)
                                                     +  list_of_net_identifiers )
                        + SEMICOLON )

    output_declaration = ( Suppress('output') + Group(    Optional(_range)
                                                       +  list_of_net_identifiers )
                        + SEMICOLON )
    
    block_item_declaration = reg_declaration # fixme - lots more to go

    block_id_and_opt_decl = Group( COLON + block_identifier                     \
                                         + ZeroOrMore(block_item_declaration) )

    seq_block = Group( Suppress('begin')                                   \
                       + Optional(block_id_and_opt_decl)                   \
                       + ZeroOrMore(statement) + Suppress('end') )



    reg_lvalue = Group(   reg_identifier_range  # e.g. reg[ 31:16 ]
                        | reg_identifier_expr   # e.g. reg[ <single_bit_expr> ]
                        | reg_identifier
                         # fixme - lots more to go
                      )

    net_lvalue = Forward()

    net_concatenation = Group( LBRACE + delimitedList(net_lvalue) + RBRACE )

    net_lvalue << Group (  net_identifier_range  # e.g. net[ 31:16 ]
                         | net_identifier_expr   # e.g. net[ <single_bit_expr> ]
                         | net_identifier
                         | net_concatenation     # e.g. { net1, net2[3], net3[4:0] {a,b}}
                        )

    # net_value is not grouped into [ 'net_value', [ net_value_obj ] ]
    #                          just: [ net_value_obj ]
    net_value = (  net_identifier_range   # e.g. net[ 31:16 ] 
                 | net_identifier_expr    # e.g. net[ <single_bit_expr> ] 
                 | net_identifier        
                 | net_concatenation     # e.g. { net1, net2[3], net3[4:0] {a,b}}
                )
    
    repeat_event_control = Suppress('repeat') # fixme. it's repeat ( expr ) event_control

    event_control = Suppress('@') # fixme... stuff after @

    delay_or_event_control = delay_control | event_control | repeat_event_control


    # ==== expression ==================================================

    invertOp = Literal('~')
    multOp   = oneOf('* /')
    plusOp   = oneOf('+ -')

# To use the operatorGrammar helper:
#   1.  Define the "atom" operand term of the grammar.
#       For this simple grammar, the smallest operand is either
#       and integer or a variable.  This will be the first argument
#       to the operatorGrammar method.
#   2.  Define a list of tuples for each level of operator
#       precendence.  Each tuple is of the form
#       (opExpr, numTerms, rightLeftAssoc, parseAction), where
#       - opExpr is the pyparsing expression for the operator;
#          may also be a string, which will be converted to a Literal
#       - numTerms is the number of terms for this operator (must
#          be 1 or 2)
#       - rightLeftAssoc is the indicator whether the operator is
#          right or left associative, using the pyparsing-defined
#          constants opAssoc.RIGHT and opAssoc.LEFT.
#       - parseAction is the parse action to be associated with 
#          expressions matching this operator expression (the
#          parse action tuple member may be omitted)
#   3.  Call operatorGrammar passing the operand expression and
#       the operator precedence list, and save the returned value
#       as the generated pyparsing expression.  You can then use
#       this expression to parse input strings, or incorporate it
#       into a larger, more complex grammar.
#       
    expr_unsigned_integer = Group(Word(nums))   
    primary = net_value | expr_unsigned_integer

    gregs_simple_expression = operatorPrecedence( primary,
                            [
                             (invertOp, 1, opAssoc.RIGHT),
                             (multOp,   2, opAssoc.LEFT),
                             (plusOp,   2, opAssoc.LEFT),
                            ] )
   
    # ==== end expression ==================================================

    expression << gregs_simple_expression # fixme

    net_assignment = Group( net_lvalue + Suppress('=') + expression )

    blocking_assignment = Group( reg_lvalue + Suppress('=')         
                                 + Optional(delay_or_event_control) 
                                 + expression )

    reg_assignment = Group( reg_lvalue + Suppress('=') + expression )

    blocking_assignment_semi = blocking_assignment + SEMICOLON

    list_of_net_assignments = Group(delimitedList(net_assignment)) 

    null_statement = Group(Literal(';'))

    statement_or_null = null_statement | statement

    continuous_assign = Group( Suppress('assign') 
                             + Optional(delay_control)
                             + list_of_net_assignments 
                             + SEMICOLON )

    procedural_timing_control_stmt = Group(delay_or_event_control + statement_or_null)

    statement << Group(   seq_block                        
                        | procedural_timing_control_stmt 
                        | blocking_assignment_semi         
                      ) # fixme - lots more to go

    initial_construct = Suppress('initial') + statement

    always_construct = Suppress('always') + statement

    module_item_declaration = ( reg_declaration                      
                              | net_declaration 
                              | input_declaration 
                              | output_declaration # fixme - lots more to go
                              )

    named_port_connection = Group( Suppress('.') 
                                 + port_identifier
                                 + LPAREN
                                 + expression 
                                 + RPAREN
                                 )

    list_of_named_port_connections = Group( delimitedList(named_port_connection) )

    list_of_module_connections = ( # list_of_ordered_port_connections | 
                                   list_of_named_port_connections )

    module_instance = Group( name_of_instance 
                           + LPAREN
                           + list_of_module_connections
                           + RPAREN     
                           )


    module_instantiation = Group( module_identifier 
                              # + Optional(parameter_value_assignment)
                                + delimitedList(module_instance)
                                + SEMICOLON
                                )

    module_item  = (   module_item_declaration
                     | initial_construct
                     | continuous_assign
                     | always_construct  
                     | module_instantiation 
                     | monitor
                     # fixme - lots more to go
                   )

    module_item_list = Group(OneOrMore(module_item))

    module_name = Group(simple_Identifier)

    module_decl = Group(
                    Suppress(Literal('module')) + module_name   
                  + Optional(list_of_ports)     + SEMICOLON     
                  + Optional(module_item_list)                  
                  + Suppress(Literal('endmodule')) )

    # ---- timescale
    time_1_10_100 = Literal('100') | Literal('10') | Literal('1')
    time_unit_string = Literal('s')  | Literal('ms') | Literal('us') |   \
                       Literal('ns') | Literal('ps') | Literal('fs')
    time_unit = Group( time_1_10_100 + time_unit_string )
    timescale = Group( Suppress(r'`timescale') + time_unit + Suppress('/') + time_unit )


    # ---- top level
    source = timescale | module_decl

    parser = OneOrMore(source)

    # actions
    # temps....
    expr_unsigned_integer.setParseAction       ( lambda t: t[0].insert(0,'uint'))

    always_construct.setParseAction       ( lambda t: t[0].insert(0,'always'))
    blocking_assignment.setParseAction    ( lambda t: t[0].insert(0,'blocking_assignment'))
    block_identifier.setParseAction       (  f_name_identifier('block_identifier'))
    block_id_and_opt_decl.setParseAction  ( lambda t: t[0].insert(0,'block_id_and_opt_decl'))
    continuous_assign.setParseAction      ( lambda t: t[0].insert(0,'continuous_assign'))
    delay_control.setParseAction          ( lambda t: t[0].insert(0,'delay_control'))
    expression.setParseAction             ( lambda t: t[0].insert(0,'expression'))
    initial_construct.setParseAction      ( lambda t: t[0].insert(0,'initial'))
    input_declaration.setParseAction      ( lambda t: t[0].insert(0,'input_declaration'))
    list_of_ports.setParseAction          ( lambda t: t[0].insert(0,'list_of_ports'))
    list_of_named_port_connections.setParseAction( lambda t: t[0].insert(0,'list_of_named_port_connections'))
    list_of_net_assignments.setParseAction( lambda t: t[0].insert(0,'list_of_net_assignments'))
    list_of_net_identifiers.setParseAction( lambda t: t[0].insert(0,'list_of_net_identifiers'))
    list_of_reg_identifiers.setParseAction( lambda t: t[0].insert(0,'list_of_reg_identifiers'))
    module_decl.setParseAction            ( lambda t: t[0].insert(0,'module_decl'))
    module_identifier.setParseAction      (  f_name_identifier('module_identifier'))
    module_instance.setParseAction        ( lambda t: t[0].insert(0,'module_instance'))
    module_instantiation.setParseAction   ( lambda t: t[0].insert(0,'module_instantiation'))
    module_item_list.setParseAction       ( lambda t: t[0].insert(0,'module_item_list'))
    module_name.setParseAction            ( lambda t: t[0].insert(0,'module_name'))
    monitor.setParseAction                ( lambda t: t[0].insert(0,'monitor'))
    name_of_instance.setParseAction       ( f_name_identifier('name_of_instance'))
    net_assignment.setParseAction         ( lambda t: t[0].insert(0,'net_assignment'))
    net_concatenation.setParseAction      ( lambda t: t[0].insert(0,'net_concatenation'))
    net_declaration.setParseAction        ( lambda t: t[0].insert(0,'net_declaration'))
    net_identifier.setParseAction         ( f_name_identifier('net_identifier'))
    net_identifier_expr.setParseAction    ( lambda t: t[0].insert(0,'net_identifier_expr'))
    net_identifier_range.setParseAction   ( lambda t: t[0].insert(0,'net_identifier_range'))
    net_lvalue.setParseAction             ( lambda t: t[0].insert(0,'net_lvalue'))
    null_statement.setParseAction         ( lambda t: t[0].insert(0,'null_statement'))
    output_declaration.setParseAction     ( lambda t: t[0].insert(0,'output_declaration'))
    _range.setParseAction                 ( lambda t: t[0].insert(0,'range'))
    param_identifier.setParseAction       ( f_name_identifier('param_identifier'))
    port_identifier.setParseAction        ( f_name_identifier('port_identifier'))
    reg_assignment.setParseAction         ( lambda t: t[0].insert(0,'reg_assignment'))
    reg_identifier.setParseAction         ( f_name_identifier('reg_identifier'))
    reg_identifier_expr.setParseAction    ( lambda t: t[0].insert(0,'reg_identifier_expr'))
    reg_identifier_range.setParseAction   ( lambda t: t[0].insert(0,'reg_identifier_range'))
    reg_lvalue.setParseAction             ( lambda t: t[0].insert(0,'reg_lvalue'))
    reg_declaration.setParseAction        ( lambda t: t[0].insert(0,'reg_declaration'))

    procedural_timing_control_stmt.setParseAction  ( lambda t: t[0].insert(0,'proc_timing_ctrl_stmt'))

    seq_block.setParseAction              ( lambda t: t[0].insert(0,'seq_block'))
    signed.setParseAction                 ( lambda t: [t] )
    statement.setParseAction              ( lambda t: t[0].insert(0,'statement'))
    timescale.setParseAction              ( lambda t: t[0].insert(0,'timescale'))
    return parser




####################################################
if __name__ == '__main__' :
    pass

# EBNF from http://www.externsoft.ch/download/verilog.html
