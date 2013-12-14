// A verilog file

module test(
            input      r,
            output reg q,
            input      clk
            );
   
  begin
     always @(posedge clk) begin q <= r; end
end

endmodule // test

