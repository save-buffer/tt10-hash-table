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

async def insert(dut, key, val):
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = key << 4 | val
    dut.uio_in.value = GO | CMD_INSERT
    await ClockCycles(dut.clk, 15)

async def lookup(dut, key):
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = key << 4
    dut.uio_in.value = GO | CMD_LOOKUP
    await ClockCycles(dut.clk, 15)

async def delete(dut, key):
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = key << 4
    dut.uio_in.value = GO | CMD_DELETE
    await ClockCycles(dut.clk, 15)

def status(dut):
    return (int(dut.uio_out) >> 6) & 0b11

def val(dut):
    return int(dut.uo_out) & 0b1111

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
    dut.uio_in.value = GO | CMD_INSERT
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == 0
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK

    dut.ui_in.value = 0x69
    await ClockCycles(dut.clk, 15)
    assert dut.uo_out.value == 0 # Make sure we don't do anything until GO
    assert (int(dut.uio_out) >> 6) & 0b11 == STATUS_OK

    dut.uio_in.value = CMD_INSERT # Bring GO low
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = GO | CMD_INSERT
    await ClockCycles(dut.clk, 10)
    assert status(dut) == STATUS_OK

    await lookup(dut, 0x4)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0x02
    
    await lookup(dut, 0x9)
    assert status(dut) == STATUS_NOTFOUND

    await delete(dut, 0x6)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0x9

    await lookup(dut, 0x6)
    assert status(dut) == STATUS_NOTFOUND

    await insert(dut, 0x4, 0x3)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0x2

    await lookup(dut, 0x4)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0x3

    for i in range(8):
        await insert(dut, i, i)
        assert status(dut) == STATUS_OK

    await insert(dut, 0xF, 0xF)
    assert status(dut) == STATUS_FULL
    
    await delete(dut, 0x5)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0x5

    await insert(dut, 0xF, 0xF)
    assert status(dut) == STATUS_OK

    await lookup(dut, 0xF)
    assert status(dut) == STATUS_OK
    assert val(dut) == 0xF

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
