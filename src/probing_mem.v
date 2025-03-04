/*
 * Copyright (c) 2024 Alexander Krassovsky
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module probing_mem (
    input wire 	      clk,
    input wire [2:0]  hash,
    input wire [3:0]  key,
    input wire [3:0]  val,
    input wire [1:0]  cmd,
    input wire 	      go,
    input wire 	      rst_n,
    output reg [1:0]  status,
    output reg [3:0]  out
);
   
   reg [8:0]   mem[0:7];
   reg [3:0]   cursor;
   reg 	       state;

   integer     i;

   localparam CMD_LOOKUP = 0;
   localparam CMD_INSERT = 1;
   localparam CMD_DELETE = 2;

   localparam STATE_IDLE = 0;
   localparam STATE_PROBING = 1;

   localparam STATUS_OK = 0;
   localparam STATUS_FULL = 1;
   localparam STATUS_NOTFOUND = 2;
   localparam STATUS_BUSY = 3;

   always @(posedge clk) begin
       if (!rst_n) begin
	   for (i = 0; i < 8; i = i + 1) begin
	       mem[i] <= 0;
	   end
	   cursor <= 0;
	   state <= STATE_IDLE;
	   status <= STATUS_OK;
	   out <= 0;
       end
       else begin
	   case (state)
	       STATE_IDLE: begin
		   if (go) begin
		       cursor <= {1'b0, hash[2:0]};
		       state <= STATE_PROBING;
		       $display("probing");
		   end
	       end
	       STATE_PROBING: begin
		   if (cursor[3] && cursor[2:0] == hash[2:0]) begin // Did a full loop
		       $display("not found");
		       status <= cmd == CMD_INSERT ? STATUS_FULL : STATUS_NOTFOUND;
		       state <= STATE_IDLE;
		   end
		   else if ((cmd == CMD_LOOKUP || cmd == CMD_DELETE) && mem[cursor[2:0]][8] && mem[cursor[2:0]][7:4] == key) begin // Found the key!
		       $display("found");
		       if (cmd == CMD_LOOKUP)
			 out <= mem[cursor[2:0]][3:0];
		       else
			 mem[cursor[2:0]][8] <= 0;
		       state <= STATE_IDLE;
		       status <= STATUS_OK;
		   end
		   else if (cmd == CMD_INSERT && !mem[cursor[2:0]][8]) begin // Found an empty slot
		       $display("inserted");
		       mem[cursor[2:0]][8] <= 1;
		       mem[cursor[2:0]][7:4] <= key;
		       mem[cursor[2:0]][3:0] <= val;
		       state <= STATE_IDLE;
		       status <= STATUS_OK;
		   end
		   else begin
		       $display("advancing");
		       cursor <= cursor + 1;
		   end
	       end
	   endcase
       end
   end
endmodule
