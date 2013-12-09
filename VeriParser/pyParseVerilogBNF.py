# Pyparsing BNF definition for verilog

from pyparsing import *

def get_verilogBNF() :

    return source_text



####################################################
if __name__ == '__main__' :

    data = """
module ; Fred Fred endmodule
    """    

    parser = get_verilogBNF()
    parseL = parser.parseString(data, True)
    print parseL
    for item in parseL : 
        print item, `item`


###  <module>
###  	::= module <name_of_module> <list_of_ports>? ;
###  		<module_item>*
###  		endmodule
###  	||= macromodule <name_of_module> <list_of_ports>? ;
###  		<module_item>*
###  		endmodule
###  
###  <name_of_module>
###  	::= <IDENTIFIER>
###  
###  <list_of_ports>
###  	::= ( <port> <,<port>>* )
###  
###  <port>
###  	::= <port_expression>?
###  	||= . <name_of_port> ( <port_expression>? )
###  
###  <port_expression>
###  	::= <port_reference>
###  	||= { <port_reference> <,<port_reference>>* }
###  
###  <port_reference>
###  	::= <name_of_variable>
###  	||= <name_of_variable> [ <constant_expression> ]
###  	||= <name_of_variable> [ <constant_expression> :<constant_expression> ]
###  
###  <name_of_port>
###  	::= <IDENTIFIER>
###  
###  <name_of_variable>
###  	::= <IDENTIFIER>
###  
###  <module_item>
###  	::= <parameter_declaration>
###  	||= <input_declaration>
###  	||= <output_declaration>
###  	||= <inout_declaration>
###  	||= <net_declaration>
###  	||= <reg_declaration>
###  	||= <time_declaration>
###  	||= <integer_declaration>
###  	||= <real_declaration>
###  	||= <event_declaration>
###  	||= <gate_declaration>
###  	||= <UDP_instantiation>
###  	||= <module_instantiation>
###  	||= <parameter_override>
###  	||= <continuous_assign>
###  	||= <specify_block>
###  	||= <initial_statement>
###  	||= <always_statement>
###  	||= <task>
###  	||= <function>
###  
###  <UDP>
###  	::= primitive <name_of_UDP> ( <name_of_variable>
###  		<,<name_of_variable>>* ) ;
###  		<UDP_declaration>+
###  		<UDP_initial_statement>?
###  		<table_definition>
###  		endprimitive
###  
###  <name_of_UDP>
###  	::= <IDENTIFIER>
###  
###  <UDP_declaration>
###  	::= <output_declaration>
###  	||= <reg_declaration>
###  	||= <input_declaration>
###  
###  <UDP_initial_statement>
###  	::= initial <output_terminal_name> = <init_val> ;
###  
###  <init_val>
###  	::= 1'b0
###  	||= 1'b1
###  	||= 1'bx
###  	||= 1'bX
###  	||= 1'B0
###  	||= 1'B1
###  	||= 1'Bx
###  	||= 1'BX
###  	||= 1
###  	||= 0
###  
###  <output_terminal_name>
###  	::= <name_of_variable>
###  
###  <table_definition>
###  	::= table <table_entries> endtable
###  
###  <table_entries>
###  	::= <combinational_entry>+
###  	||= <sequential_entry>+
###  
###  <combinational_entry>
###  	::= <level_input_list> : <OUTPUT_SYMBOL> ;
###  
###  <sequential_entry>
###  	::= <input_list> : <state> : <next_state> ;
###  
###  <input_list>
###  	::= <level_input_list>
###  	||= <edge_input_list>
###  
###  <level_input_list>
###  	::= <LEVEL_SYMBOL>+
###  
###  <edge_input_list>
###  	::= <LEVEL_SYMBOL>* <edge> <LEVEL_SYMBOL>*
###  
###  <edge>
###  	::= ( <LEVEL_SYMBOL> <LEVEL_SYMBOL> )
###  	||= <EDGE_SYMBOL>
###  
###  <state>
###  	::= <LEVEL_SYMBOL>
###  
###  <next_state>
###  	::= <OUTPUT_SYMBOL>
###  	||= - (This is a literal hyphen, see Chapter 5 for details).
###  
###  <OUTPUT_SYMBOL> is one of the following characters:
###  	0   1   x   X
###  
###  <LEVEL_SYMBOL> is one of the following characters:
###  	0   1   x   X   ?   b   B
###  
###  <EDGE_SYMBOL> is one of the following characters:
###  	r   R   f   F   p   P   n   N   *
###  
###  
###  <task>
###  	::= task <name_of_task> ;
###  		<tf_declaration>*
###  		<statement_or_null>
###  		endtask
###  
###  <name_of_task>
###  	::= <IDENTIFIER>
###  
###  <function>
###  	::= function <range_or_type>? <name_of_function> ;
###  		<tf_declaration>+
###  		<statement>
###  		endfunction
###  
###  <range_or_type>
###  	::= <range>
###  	||= integer
###  	||= real
###  
###  <name_of_function>
###  	::= <IDENTIFIER>
###  
###  <tf_declaration>
###  	::= <parameter_declaration>
###  	||= <input_declaration>
###  	||= <output_declaration>
###  	||= <inout_declaration>
###  	||= <reg_declaration>
###  	||= <time_declaration>
###  	||= <integer_declaration>
###   	||= <real_declaration>
