`timescale 1ns / 1ps
`define DATA_W 32
`define ADDR_W 4
module iob_ram_sp_be_tb;
 reg clk;
 reg en; 
 reg [`DATA_W/8-1:0] we; 
 reg [`ADDR_W-1:0] addr;
 reg [`DATA_W-1:0] data_in;
 reg [`DATA_W-1:0] data_out;
 integer i, seq_ini;
 parameter clk_per = 10; 
 initial begin
`ifdef VCD
 $dumpfile("uut.vcd");
 $dumpvars();
`endif
 clk = 1;
 en = 0;
 for(i=0; i<`DATA_W/8; i = i + 1)
 we[i] = 0;
 addr = 0;
 seq_ini = 32;
 #clk_per;
 @(posedge clk) #1;
 en = 1;
 @(posedge clk) #1;
 for(i = 0; i < 2**`ADDR_W; i = i + 1) begin
 we[i] = 1;
 @(posedge clk) #1;
 addr = i;
 data_in = i+seq_ini;
 @(posedge clk) #1;
 end
 @(posedge clk) #1;
 for(i = 0; i < `DATA_W/8; i = i + 1)
 we = 0;
 @(posedge clk) #1;
 for(i = 0; i < 2**`ADDR_W; i = i + 1) begin
 addr = i;
 @(posedge clk) #1;
 if(i+seq_ini != data_out) begin
 $display("ERROR: write error in position %d, where data=%h but data_out=%h", i, i+seq_ini, data_out);
 $finish;
 end
 end
 seq_ini = 64;
 for(i = 0; i < 2**`ADDR_W; i = i + 1) begin
 addr = i;
 @(posedge clk) #1;
 if(i+seq_ini == data_out) begin
 $display("ERROR: read error in position %d, where data and data_out are '%h' but should not be the same", i, data_out);
 $finish;
 end
 end
 @(posedge clk) #1;
 en = 0;
 #clk_per;
 $display("%c[1;34m",27);
 $display("Test completed successfully.");
 $display("%c[0m",27);
 #(5*clk_per) $finish;
 end
 iob_ram_sp_be
 #(
 .DATA_W(`DATA_W),
 .ADDR_W(`ADDR_W)
 )
 uut
 (
 .clk(clk),
 .en(en),
 .we(we),
 .addr(addr),
 .din(data_in),
 .dout(data_out)
 );
 always #(clk_per/2) clk = ~clk; 
endmodule