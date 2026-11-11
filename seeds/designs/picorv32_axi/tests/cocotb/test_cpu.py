"""Exercise the AXI CPU with the upstream testbench_ez program."""

import cocotb
from cocotb.triggers import Timer


@cocotb.test(timeout_time=20, timeout_unit="us")
async def increments_memory(dut):
    """Check the counter program through independent AXI address and data channels."""
    # Six instruction words from PicoRV32 testbench_ez.v (public domain).
    memory = dict(enumerate((
        0x3FC00093, 0x0000A023, 0x0000A103,
        0x00110113, 0x0020A023, 0xFF5FF06F,
    )))
    stores = []
    write_address = None
    write_payload = None
    write_response = False
    read_data = None
    dut.clk.value = 0
    dut.resetn.value = 0
    dut.irq.value = 0
    dut.pcpi_wr.value = 0
    dut.pcpi_rd.value = 0
    dut.pcpi_wait.value = 0
    dut.pcpi_ready.value = 0

    for cycle in range(600):
        dut.clk.value = 0
        active = cycle >= 4
        dut.resetn.value = int(active)
        aw_ready = active and write_address is None and not write_response and cycle % 2 == 0
        w_ready = active and write_payload is None and not write_response and cycle % 2 == 1
        ar_ready = active and read_data is None and cycle % 3 == 0
        dut.mem_axi_awready.value = int(aw_ready)
        dut.mem_axi_wready.value = int(w_ready)
        dut.mem_axi_arready.value = int(ar_ready)
        dut.mem_axi_bvalid.value = int(write_response)
        dut.mem_axi_rvalid.value = int(read_data is not None)
        dut.mem_axi_rdata.value = read_data if read_data is not None else 0
        await Timer(5, unit="ns")

        if write_response and int(dut.mem_axi_bready.value):
            write_response = False
        if read_data is not None and int(dut.mem_axi_rready.value):
            read_data = None
        if aw_ready and int(dut.mem_axi_awvalid.value):
            write_address = int(dut.mem_axi_awaddr.value)
        if w_ready and int(dut.mem_axi_wvalid.value):
            write_payload = (int(dut.mem_axi_wdata.value), int(dut.mem_axi_wstrb.value))
        if ar_ready and int(dut.mem_axi_arvalid.value):
            address = int(dut.mem_axi_araddr.value)
            assert address % 4 == 0
            read_data = memory[address // 4]
        if write_address is not None and write_payload is not None:
            word, strobe = write_payload
            assert write_address == 0x3FC and strobe == 0xF
            assert word == len(stores)
            memory[write_address // 4] = word
            stores.append(word)
            write_address = None
            write_payload = None
            write_response = True

        dut.clk.value = 1
        await Timer(5, unit="ns")
        assert not int(dut.trap.value)
        if len(stores) == 5 and not write_response:
            return

    raise AssertionError(f"Expected five acknowledged counter stores, got {stores}")
