/* Test macro definitions */
`define    multi_line_def ( 123 + \
5 / 22 ) \
  + 2  

`define    multi_line_def ( 123 + \
                            ff
`define blank
`define macro_w_params(x, param2, p3  ) x "`x" param2 + p3
`blank`blank
multi_line_def is `multi_line_def
`macro_w_params(1,2,3)
// No line after next one!                            
`define macro unterminated - will return error \
