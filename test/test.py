# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

CMD_LOOKUP = 0x0
CMD_INSERT = 0x1
CMD_DELETE = 0x2

STATUS_OK = 0
STATUS_FULL = 1
STATUS_NOTFOUND = 2
STATUS_BUSY = 3

GO = (1 << 2)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    dut.ui_in.value = 0x42
    dut.uio_in.value = CMD_INSERT
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == 0
    dut.ui_in.value = GO | CMD_INSERT
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == 0
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK

    dut.ui_in.value = 0x69
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == 0
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK
    dut.uio_in.value = CMD_INSERT # Bring GO low
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = GO | CMD_INSERT
    await ClockCycles(dut.clk, 10)
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK

    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = 0x40
    dut.uio_in.value = GO | CMD_LOOKUP
    await ClockCycles(dut.clk, 10)
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK
    assert dut.uo_out.value == 0x02
    
    

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
