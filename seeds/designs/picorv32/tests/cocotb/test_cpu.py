"""Exercise the native memory interface with the upstream testbench_ez program."""

import cocotb
from cocotb.triggers import Timer


@cocotb.test(timeout_time=20, timeout_unit="us")
async def increments_memory(dut):
    """Check instruction fetch, data reads, and the resulting counter stores."""
    # Six instruction words from PicoRV32 testbench_ez.v (public domain).
    memory = dict(enumerate((
        0x3FC00093, 0x0000A023, 0x0000A103,
        0x00110113, 0x0020A023, 0xFF5FF06F,
    )))
    stores = []
    dut.clk.value = 0
    dut.resetn.value = 0
    dut.mem_ready.value = 0
    dut.mem_rdata.value = 0
    dut.irq.value = 0
    dut.pcpi_wr.value = 0
    dut.pcpi_rd.value = 0
    dut.pcpi_wait.value = 0
    dut.pcpi_ready.value = 0

    for cycle in range(500):
        dut.clk.value = 0
        dut.resetn.value = int(cycle >= 4)
        dut.mem_ready.value = 0
        await Timer(2, unit="ns")
        if cycle >= 4 and int(dut.mem_valid.value):
            address = int(dut.mem_addr.value)
            strobe = int(dut.mem_wstrb.value)
            assert address % 4 == 0
            if strobe:
                assert address == 0x3FC and strobe == 0xF
                word = int(dut.mem_wdata.value)
                assert word == len(stores)
                memory[address // 4] = word
                stores.append(word)
            else:
                dut.mem_rdata.value = memory[address // 4]
            dut.mem_ready.value = 1
        await Timer(3, unit="ns")
        dut.clk.value = 1
        await Timer(5, unit="ns")
        assert not int(dut.trap.value)
        if len(stores) == 5:
            return

    raise AssertionError(f"Expected five counter stores, got {stores}")
