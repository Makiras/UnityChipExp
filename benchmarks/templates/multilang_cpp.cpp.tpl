#include "{{HEADER_NAME}}"

#include <chrono>
#include <cstdio>
#include <memory>

namespace {
constexpr int kWarmupSteps = {{WARMUP_STEPS}};
constexpr int kBenchSteps = {{BENCH_STEPS}};
}

int main() {
    auto dut = std::make_unique<{{DUT_CLASS}}>();
    dut->reset.AsImmWrite();
    dut->reset = 1;
    dut->InitClock("clock");
    dut->Step(kWarmupSteps);

    const auto start = std::chrono::steady_clock::now();
    dut->Step(kBenchSteps);
    const auto end = std::chrono::steady_clock::now();

    const double elapsed_ms =
        std::chrono::duration<double, std::milli>(end - start).count();
    const double speed =
        elapsed_ms <= 0.0 ? 0.0 : (static_cast<double>(kBenchSteps) * 1000.0 / elapsed_ms);

    std::printf("bench_warmup_steps=%d\n", kWarmupSteps);
    std::printf("bench_steps=%d\n", kBenchSteps);
    std::printf("bench_elapsed_ms=%.6f\n", elapsed_ms);
    std::printf("bench_speed_cycles_per_s=%.6f\n", speed);

    dut->Finish();
    return 0;
}
