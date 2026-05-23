module core (clk, rst, dout);
  input clk, rst;
  output dout;
  wire alu0_out, alu1_out, alu2_out, alu3_out;
  wire mux0_out, mux1_out;
  alu u_alu_0 (.clk(clk), .rst(rst), .dout(alu0_out));
  alu u_alu_1 (.clk(clk), .rst(rst), .dout(alu1_out));
  alu u_alu_2 (.clk(clk), .rst(rst), .dout(alu2_out));
  alu u_alu_3 (.clk(clk), .rst(rst), .dout(alu3_out));
  NAND2 u_nand0 (.A(alu0_out), .B(alu1_out), .Y(mux0_out));
  NAND2 u_nand1 (.A(alu2_out), .B(alu3_out), .Y(mux1_out));
  NOR2 u_nor0 (.A(mux0_out), .B(mux1_out), .Y(dout));
endmodule
