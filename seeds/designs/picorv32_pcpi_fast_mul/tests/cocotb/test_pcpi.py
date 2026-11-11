"""Check the standalone PicoRV32 PCPI multiplication result and handshake."""

import cocotb
from cocotb.triggers import Timer


async def _tick(dut):
    """Advance one cycle and let registered outputs settle."""
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")


@cocotb.test(timeout_time=20, timeout_unit="us")
async def completes_rv32m_operations(dut):
    """Drive encoded instructions and check each result with a bounded wait."""
    # funct3, rs1, rs2, expected result
    vectors = (
        (0, 0xFFFFFFFF, 2, 0xFFFFFFFE),  # MUL
        (0, 0, 0xFFFFFFFF, 0),
        (1, 0x80000000, 2, 0xFFFFFFFF),  # MULH
        (1, 0x80000000, 0xFFFFFFFF, 0),
        (2, 0x80000000, 0xFFFFFFFF, 0x80000000),  # MULHSU
        (3, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFE),  # MULHU
    )

    dut.resetn.value = 0
    dut.pcpi_valid.value = 0
    dut.pcpi_insn.value = 0
    dut.pcpi_rs1.value = 0
    dut.pcpi_rs2.value = 0
    for _ in range(4):
        await _tick(dut)
    dut.resetn.value = 1

    # An ordinary RV32I ADD must never complete on the RV32M coprocessor.
    dut.pcpi_insn.value = 0x33
    dut.pcpi_valid.value = 1
    for _ in range(4):
        await _tick(dut)
        assert not int(dut.pcpi_ready.value)
        assert not int(dut.pcpi_wait.value)
    dut.pcpi_valid.value = 0
    await _tick(dut)

    for funct3, rs1, rs2, expected in vectors:
        dut.pcpi_insn.value = 0x02000033 | (funct3 << 12)
        dut.pcpi_rs1.value = rs1
        dut.pcpi_rs2.value = rs2
        dut.pcpi_valid.value = 1
        for _ in range(80):
            await _tick(dut)
            if int(dut.pcpi_ready.value):
                assert int(dut.pcpi_wr.value)
                actual = int(dut.pcpi_rd.value)
                assert actual == expected, (
                    f"funct3={funct3}, rs1={rs1:#010x}, rs2={rs2:#010x}: "
                    f"expected {expected:#010x}, got {actual:#010x}"
                )
                break
        else:
            raise AssertionError(f"No PCPI completion for funct3={funct3}")

        # Hold the request through the edge that consumes the response.
        await _tick(dut)
        dut.pcpi_valid.value = 0
        for _ in range(4):
            await _tick(dut)
        assert not int(dut.pcpi_ready.value)
        assert not int(dut.pcpi_wait.value)
