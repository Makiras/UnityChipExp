import toffee
import random
from toffee.triggers import ClockCycles
from UT_CoupledL2 import DUTCoupledL2
from bundle import TileLinkBundle
from agent import TileLinkAgent


async def test_top(dut: DUTCoupledL2):
    toffee.start_clock(dut)

    dut.reset.value = 1
    await ClockCycles(dut, 100)
    dut.reset.value = 0

    tlbundle = TileLinkBundle.from_prefix("master_port_0_0_").bind(dut)
    tlbundle.set_all(0)
    tlagent = TileLinkAgent(tlbundle)

    await ClockCycles(dut, 20)
    ref_data = [0] * 0x10

    for _ in range(4000):
        # Read
        address = random.randint(0, 0xF) << 6
        r_data = await tlagent.aquire_block(address)
        print(f"Read {address} = {hex(r_data)}")
        assert r_data == ref_data[address >> 6]

        # Write
        send_data = random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        await tlagent.release_data(address, send_data)
        ref_data[address >> 6] = send_data
        print(f"Write {address} = {hex(send_data)}")


if __name__ == "__main__":
    toffee.setup_logging(toffee.INFO)
    dut = DUTCoupledL2(["+verilator+rand+reset+0"])
    dut.InitClock("clock")
    dut.reset.AsImmWrite()

    toffee.run(test_top(dut))

    dut.Finish()
