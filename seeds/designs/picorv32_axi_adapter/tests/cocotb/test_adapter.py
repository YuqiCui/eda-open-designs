"""Check standalone native-to-AXI translation under backpressure."""

import cocotb
from cocotb.triggers import Timer


async def _tick(dut):
    """Advance one cycle and let registered outputs settle."""
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")


@cocotb.test(timeout_time=2, timeout_unit="us")
async def independently_handshakes_axi_channels(dut):
    """Check both write channel orders, response delay, and instruction reads."""
    dut.resetn.value = 0
    dut.mem_valid.value = 0
    dut.mem_addr.value = 0
    dut.mem_wdata.value = 0
    dut.mem_wstrb.value = 0
    dut.mem_instr.value = 0
    dut.mem_axi_awready.value = 0
    dut.mem_axi_wready.value = 0
    dut.mem_axi_bvalid.value = 0
    dut.mem_axi_arready.value = 0
    dut.mem_axi_rvalid.value = 0
    dut.mem_axi_rdata.value = 0
    for _ in range(3):
        await _tick(dut)
    dut.resetn.value = 1
    # The adapter clears its AR and W acknowledgment flags on an idle cycle.
    await _tick(dut)

    for address_first, address in ((True, 0x100), (False, 0x104)):
        dut.mem_valid.value = 1
        dut.mem_addr.value = address
        dut.mem_wdata.value = 0xCAFEBABE
        dut.mem_wstrb.value = 0x5
        await _tick(dut)
        assert int(dut.mem_axi_awvalid.value)
        assert int(dut.mem_axi_wvalid.value)
        assert int(dut.mem_axi_awaddr.value) == address
        assert int(dut.mem_axi_wdata.value) == 0xCAFEBABE
        assert int(dut.mem_axi_wstrb.value) == 0x5
        assert not int(dut.mem_ready.value)

        dut.mem_axi_awready.value = int(address_first)
        dut.mem_axi_wready.value = int(not address_first)
        await _tick(dut)
        assert int(dut.mem_axi_awvalid.value) == int(not address_first)
        assert int(dut.mem_axi_wvalid.value) == int(address_first)
        dut.mem_axi_awready.value = int(not address_first)
        dut.mem_axi_wready.value = int(address_first)
        await _tick(dut)
        assert not int(dut.mem_axi_awvalid.value)
        assert not int(dut.mem_axi_wvalid.value)
        assert not int(dut.mem_ready.value)

        dut.mem_axi_awready.value = 0
        dut.mem_axi_wready.value = 0
        dut.mem_axi_bvalid.value = 1
        await Timer(1, unit="ns")
        assert int(dut.mem_axi_bready.value) and int(dut.mem_ready.value)
        await _tick(dut)
        dut.mem_valid.value = 0
        dut.mem_axi_bvalid.value = 0
        await _tick(dut)

    dut.mem_valid.value = 1
    dut.mem_addr.value = 0x200
    dut.mem_instr.value = 1
    dut.mem_wstrb.value = 0
    await _tick(dut)
    assert int(dut.mem_axi_arvalid.value)
    assert int(dut.mem_axi_araddr.value) == 0x200
    assert int(dut.mem_axi_arprot.value) == 4
    assert not int(dut.mem_ready.value)
    dut.mem_axi_arready.value = 1
    await _tick(dut)
    assert not int(dut.mem_axi_arvalid.value)
    assert not int(dut.mem_ready.value)

    dut.mem_axi_arready.value = 0
    dut.mem_axi_rvalid.value = 1
    dut.mem_axi_rdata.value = 0x12345678
    await Timer(1, unit="ns")
    assert int(dut.mem_axi_rready.value) and int(dut.mem_ready.value)
    assert int(dut.mem_rdata.value) == 0x12345678
    await _tick(dut)
