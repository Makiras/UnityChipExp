#include "{{VERILATOR_CLASS}}.h"
#include "{{VERILATOR_CLASS}}__Syms.h"
#include "{{ROOT_CLASS}}.h"

#include <chrono>
#include <cstdio>
#include <memory>

namespace {
constexpr int kWarmupSteps = {{WARMUP_STEPS}};
constexpr int kBenchSteps = {{BENCH_STEPS}};
}

int main(int argc, char* argv[]) {
    Verilated::commandArgs(argc, argv);

    auto dut = std::make_unique<{{VERILATOR_CLASS}}>();
    {{ROOT_CLASS}}* sigs = dut->rootp;
    sigs->{{TOP_PREFIX}}reset = 1;
    for (int i = 0; i < kWarmupSteps; ++i) {
        sigs->{{TOP_PREFIX}}clock = 0;
        dut->eval();
        sigs->{{TOP_PREFIX}}clock = 1;
        dut->eval();
    }

    const auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < kBenchSteps; ++i) {
        sigs->{{TOP_PREFIX}}clock = 0;
        dut->eval();
        sigs->{{TOP_PREFIX}}clock = 1;
        dut->eval();
    }
    const auto end = std::chrono::steady_clock::now();

    const double elapsed_ms =
        std::chrono::duration<double, std::milli>(end - start).count();
    const double speed =
        elapsed_ms <= 0.0 ? 0.0 : (static_cast<double>(kBenchSteps) * 1000.0 / elapsed_ms);

    std::printf("bench_warmup_steps=%d\n", kWarmupSteps);
    std::printf("bench_steps=%d\n", kBenchSteps);
    std::printf("bench_elapsed_ms=%.6f\n", elapsed_ms);
    std::printf("bench_speed_cycles_per_s=%.6f\n", speed);
    return 0;
}
