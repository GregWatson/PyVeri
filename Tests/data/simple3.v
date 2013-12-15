/* Test macro definitions */
`define    multi_line_def ( 123 + \
5 / 22 ) \
  + 2  

`define    multi_line_def ( 123 + \
                            ff

`define macro_w_params(x, param2, p3  ) x "`x" param2 + p3

`define macro unterminated - will return error \
