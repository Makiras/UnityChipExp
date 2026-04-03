package main

import (
	"fmt"
	ut "{{GO_IMPORT}}"
	"time"
)

const warmupSteps = {{WARMUP_STEPS}}
const benchSteps = {{BENCH_STEPS}}

func main() {
	dut := ut.New{{GO_CLASS}}()
	dut.InitClock("clock")
	dut.Reset.AsImmWrite()
	dut.Reset.Set(1)
	dut.Step(warmupSteps)

	start := time.Now()
	dut.Step(benchSteps)
	elapsed := time.Since(start)

	elapsedMs := float64(elapsed) / float64(time.Millisecond)
	speed := 0.0
	if elapsed > 0 {
		speed = float64(benchSteps) / elapsed.Seconds()
	}

	fmt.Printf("bench_warmup_steps=%d\n", warmupSteps)
	fmt.Printf("bench_steps=%d\n", benchSteps)
	fmt.Printf("bench_elapsed_ms=%.6f\n", elapsedMs)
	fmt.Printf("bench_speed_cycles_per_s=%.6f\n", speed)

	dut.Finish()
}
