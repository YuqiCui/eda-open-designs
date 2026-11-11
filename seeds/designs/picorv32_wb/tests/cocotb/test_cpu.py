"""Exercise the Wishbone CPU with the upstream testbench_ez program."""

import cocotb
from cocotb.triggers import Timer


@cocotb.test(timeout_time=20, timeout_unit="us")
async def increments_memory(dut):
    """Check counter stores through a Wishbone slave with delayed acknowledgments."""
    # Six instruction words from PicoRV32 testbench_ez.v (public domain).
    memory = dict(enumerate((
        0x3FC00093, 0x0000A023, 0x0000A103,
        0x00110113, 0x0020A023, 0xFF5FF06F,
    )))
    stores = []
    pending = False
    dut.wb_clk_i.value = 0
    dut.wb_rst_i.value = 1
    dut.wbm_ack_i.value = 0
    dut.wbm_dat_i.value = 0
    dut.irq.value = 0
    dut.pcpi_wr.value = 0
    dut.pcpi_rd.value = 0
    dut.pcpi_wait.value = 0
    dut.pcpi_ready.value = 0

    for cycle in range(500):
        dut.wb_clk_i.value = 0
        dut.wb_rst_i.value = int(cycle < 4)
        dut.wbm_ack_i.value = 0
        await Timer(2, unit="ns")
        active = cycle >= 4 and int(dut.wbm_cyc_o.value) and int(dut.wbm_stb_o.value)
        if active and pending:
            address = int(dut.wbm_adr_o.value)
            assert address % 4 == 0
            if int(dut.wbm_we_o.value):
                assert address == 0x3FC and int(dut.wbm_sel_o.value) == 0xF
                word = int(dut.wbm_dat_o.value)
                assert word == len(stores)
                memory[address // 4] = word
                stores.append(word)
            else:
                dut.wbm_dat_i.value = memory[address // 4]
            dut.wbm_ack_i.value = 1
            pending = False
        else:
            pending = bool(active)
        await Timer(3, unit="ns")
        dut.wb_clk_i.value = 1
        await Timer(5, unit="ns")
        assert not int(dut.trap.value)
        if len(stores) == 5:
            return

    raise AssertionError(f"Expected five counter stores, got {stores}")
