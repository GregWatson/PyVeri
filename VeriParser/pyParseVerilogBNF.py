# Pyparsing BNF definition for verilog

from pyparsing import *

def new_Verilog_EBNF_parser() :

    simple_Identifier = Word(alphas+"_", alphanums+"_$")

    parser = simple_Identifier

    return parser



####################################################
if __name__ == '__main__' :

    data = """
module ; Fred Fred endmodule

    """    

    data = r'stop_99$'

    parser = new_Verilog_EBNF_parser()
    parseL = parser.parseString(data, True)
    print parseL
    for item in parseL : 
        print item, `item`

# EBNF from http://www.externsoft.ch/download/verilog.html
