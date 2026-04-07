import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import time


WARMUP_STEPS = 1000
BENCH_STEPS = 5000

@cocotb.test()
async def dff_simple_test(dut):
    dut.reset.value = 1
    dut.clock.value = 0
    clock = Clock(dut.clock, 2, units="ps")

    await Timer(1, units="ps")
    cocotb.start_soon(clock.start(start_high=False))
    for _ in range(WARMUP_STEPS):
        await RisingEdge(dut.clock)

    start = time.perf_counter()
    for _ in range(BENCH_STEPS):
        await RisingEdge(dut.clock)
    elapsed_s = time.perf_counter() - start

    print(f"bench_warmup_steps={WARMUP_STEPS}")
    print(f"bench_steps={BENCH_STEPS}")
    print(f"bench_elapsed_ms={elapsed_s * 1000.0:.6f}")
    speed = 0.0 if elapsed_s <= 0.0 else BENCH_STEPS / elapsed_s
    print(f"bench_speed_cycles_per_s={speed:.6f}")
