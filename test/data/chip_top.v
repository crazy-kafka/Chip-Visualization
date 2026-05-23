module chip_top (clk, rst, out_0, out_1, out_2, out_3);
  input clk, rst;
  output out_0, out_1, out_2, out_3;
  wire core0_out, core1_out, core2_out, core3_out;
  core u_core_0 (.clk(clk), .rst(rst), .dout(core0_out));
  core u_core_1 (.clk(clk), .rst(rst), .dout(core1_out));
  core u_core_2 (.clk(clk), .rst(rst), .dout(core2_out));
  core u_core_3 (.clk(clk), .rst(rst), .dout(core3_out));
  BUFX2 u_buf_top (.A(core0_out), .Y(out_0));
endmodule
