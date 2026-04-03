import os
import sys
import time

from __init__ import *


BENCH_STEPS = {{BENCH_STEPS}}
WARMUP_STEPS = {{WARMUP_STEPS}}


if __name__ == "__main__":
    dut = {{DUT_CLASS}}()
    dut.reset.AsImmWrite()
    dut.reset.value = 1
    dut.InitClock("clock")

    dut.Step(WARMUP_STEPS)

    start = time.perf_counter()
    dut.Step(BENCH_STEPS)
    elapsed_s = time.perf_counter() - start

    print(f"bench_warmup_steps={WARMUP_STEPS}", flush=True)
    print(f"bench_steps={BENCH_STEPS}", flush=True)
    print(f"bench_elapsed_ms={elapsed_s * 1000.0:.6f}", flush=True)
    speed = 0.0 if elapsed_s <= 0.0 else BENCH_STEPS / elapsed_s
    print(f"bench_speed_cycles_per_s={speed:.6f}", flush=True)

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
