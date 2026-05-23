module sub (clk, sig_out);
  input clk;
  output sig_out;
  wire n1, n2;
  BUFX2 BUFX2_inst (.A(clk), .Y(n1));
  DFF DFF_inst (.D(n1), .CK(clk), .Q(n2));
  NAND2 NAND2_inst (.A(n1), .B(n2), .Y(sig_out));
endmodule
