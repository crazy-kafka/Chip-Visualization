module alu (clk, rst, dout);
  input clk, rst;
  output dout;
  wire sum_out, buf0_out, buf1_out, dff_q, inv_out, nand0_out, nand1_out;
  adder u_adder (.clk(clk), .rst(rst), .sum(sum_out));
  BUFX2 u_buf_lo (.A(sum_out), .Y(buf0_out));
  BUFX2 u_buf_hi (.A(buf0_out), .Y(buf1_out));
  DFF u_dff_0 (.D(buf1_out), .CK(clk), .Q(dff_q));
  INV u_inv_0 (.A(rst), .Y(inv_out));
  NAND2 u_nand2 (.A(dff_q), .B(inv_out), .Y(nand0_out));
  NAND2 u_nand3 (.A(nand0_out), .B(sum_out), .Y(nand1_out));
  BUFX2 u_buf_out (.A(nand1_out), .Y(dout));
endmodule
