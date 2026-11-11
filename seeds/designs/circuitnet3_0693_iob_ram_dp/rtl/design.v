`timescale 1ns/1ps
module iob_ram_dp
 #(
 parameter HEXFILE = "none",
 parameter DATA_W = 8,
 parameter ADDR_W = 6
 )
 (
 input clk,
 input [DATA_W-1:0] dinA,
 input [ADDR_W-1:0] addrA,
 input enA,
 input weA,
 output reg [DATA_W-1:0] doutA,
 input [DATA_W-1:0] dinB,
 input [ADDR_W-1:0] addrB,
 input enB,
 input weB,
 output reg [DATA_W-1:0] doutB
 );
 localparam mem_init_file_int = HEXFILE;
 reg [DATA_W-1:0] ram[2**ADDR_W-1:0];
 initial
 if(mem_init_file_int != "none")
 $readmemh(mem_init_file_int, ram, 0, 2**ADDR_W - 1);
 always @ (posedge clk) begin
 if (enA)
 if (weA)
 ram[addrA] <= dinA;
 `ifdef IS_CYCLONEV
 else
 `endif
 doutA <= ram[addrA];
 end
 always @ (posedge clk) begin 
 if (enB)
 if (weB)
 ram[addrB] <= dinB;
 `ifdef IS_CYCLONEV
 else
 `endif
 doutB <= ram[addrB];
 end
endmodule