/*
 * Copyright (c) 2024 Alexander Krassovsky
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Github username is save-buffer
module tt_um_save_buffer_hash_table (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
   assign uio_oe[0] = 0;
   assign uio_oe[1] = 0;
   assign uio_oe[2] = 0;
   assign uio_oe[5:3] = 0;
   assign uio_oe[6] = 1;
   assign uio_oe[7] = 1;

   wire [1:0] 	      cmd = uio_in[1:0];
   wire 	      go = uio_in[2];

   reg [1:0] 	      status;
   assign uio_out[7:6] = status;
   assign uio_out[5:0] = 0;

   wire [3:0] 	      key = ui_in[7:4];
   wire [3:0] 	      val = ui_in[3:0];
   wire [2:0] 	      hash = key[3:1] ^ (key[2:0] & {key[3], key[3], key[3]});

   reg [3:0] 	      out;
   assign uo_out[3:0] = out[3:0];
   assign uo_out[7:4] = 0;

   probing_mem tb (
       .clk(clk),
       .hash(hash),
       .key(key),
       .val(val),
       .cmd(cmd),
       .go(go),
       .rst_n(rst_n),
       .status(status),
       .out(out)
   );

   // List all unused inputs to prevent warnings
   wire _unused = &{ena, 1'b0};

endmodule
