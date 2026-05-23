module adder (clk, rst, sum);
  input clk, rst;
  output sum;
  wire n0, n1, n2, n3, n4, n5, n6, n7, n8;
  BUFX2 u_buf_a  (.A(clk),    .Y(n0));
  BUFX2 u_buf_b  (.A(n0),     .Y(n1));
  BUFX2 u_buf_c  (.A(n1),     .Y(n2));
  DFF   u_dff_a  (.D(n2),     .CK(clk), .Q(n3));
  INV   u_inv_a  (.A(n3),     .Y(n4));
  INV   u_inv_b  (.A(rst),    .Y(n5));
  NAND2 u_nand_a (.A(n4),     .B(n5),   .Y(n6));
  NAND2 u_nand_b (.A(n6),     .B(n3),   .Y(n7));
  MUX2  u_mux_a  (.A(n7),     .B(n3),   .S(clk), .Y(n8));
  NOR2  u_nor_a  (.A(n8),     .B(rst),  .Y(sum));
endmodule
