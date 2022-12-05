module test_module ( sig_a, sig_b,
        sig_c, sig_d, sig_e );
  input [15:0] sig_a;
  input [15:0] sig_b;
  output [3:0] sig_c, sig_d;
  output sig_e;
  wire  n0, n1, n2, n3, n4, n5, n6, n7,
        n8, n9, n10, n11, n12, n13, n14;
  STDCELL0 U0 ( .a(sig_a[0]), .b(sig_a[b]), .c(sig_e) );
endmodule