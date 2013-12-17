/* Test macro definitions */
`define    multi_line_def ( 123 + \
5 / 22 ) \
  + 2  

`define    multi_line_def ( 123 + \
                            ff
`define blank
`define macro_w_params(x, param2, p3  ) x "`x" param2 + p3
`blank`blank

`define multi_arg(x,y) (x+y)
`multi_arg((a+b),d[10:0])
                            
// No line after next one!                            
`define macro unterminated - will return error \
