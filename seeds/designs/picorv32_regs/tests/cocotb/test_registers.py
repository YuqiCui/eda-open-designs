"""Check the standalone PicoRV32 register file."""

import cocotb
from cocotb.triggers import Timer


async def _write_cycle(dut, address, value, *, enabled=True):
    """Drive a register write and complete one clock cycle."""
    dut.clk.value = 0
    dut.wen.value = int(enabled)
    dut.waddr.value = address
    dut.wdata.value = value
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")


@cocotb.test(timeout_time=2, timeout_unit="us")
async def dual_reads_and_write_enable(dut):
    """Check every implemented slot, the address alias, and disabled writes."""
    expected = {address: 0xABCD0000 | address for address in range(1, 32)}
    dut.raddr1.value = 1
    dut.raddr2.value = 1
    for address, value in expected.items():
        await _write_cycle(dut, address, value)

    await _write_cycle(dut, 32 | 7, 0x12345678)
    expected[7] = 0x12345678
    await _write_cycle(dut, 7, 0xFFFFFFFF, enabled=False)
    for address in expected:
        other_address = 32 - address
        dut.raddr1.value = address
        dut.raddr2.value = 32 | other_address
        await Timer(1, unit="ns")
        assert int(dut.rdata1.value) == expected[address]
        assert int(dut.rdata2.value) == expected[other_address]
