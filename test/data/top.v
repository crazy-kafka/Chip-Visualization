module top (clk, out);
  input clk;
  output out;
  wire n0;
  sub u_sub (.clk(clk), .sig_out(n0));
  BUFX2 u_buf (.A(n0), .Y(out));
endmodule
