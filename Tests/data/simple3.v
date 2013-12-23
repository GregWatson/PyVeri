/* Test macro definitions. Used in unit tests in PreProcess */
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
`define m2 (3+{{2}[5:2]})
`define m3 99.6                             
`multi_arg(`m2,`m3)+`multi_arg(5,9) // test repeated subs

`define str1 "a string // really!"
$display($time, `str1);                            
`undef m4
`undef m2

// No line after next one!                            
`define macro unterminated - will return error \
