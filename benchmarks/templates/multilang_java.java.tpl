package {{JAVA_PACKAGE}};

public class example {
    private static final int WARMUP_STEPS = {{WARMUP_STEPS}};
    private static final int BENCH_STEPS = {{BENCH_STEPS}};

    public static void main(String[] args) {
        {{JAVA_CLASS}} dut = new {{JAVA_CLASS}}();
        dut.reset.AsImmWrite();
        dut.reset.Set(1);
        dut.InitClock("clock");
        dut.Step(WARMUP_STEPS);

        long startNs = System.nanoTime();
        dut.Step(BENCH_STEPS);
        long elapsedNs = System.nanoTime() - startNs;

        double elapsedMs = elapsedNs / 1_000_000.0;
        double speed = elapsedNs <= 0 ? 0.0 : (BENCH_STEPS * 1_000_000_000.0) / elapsedNs;

        System.out.printf("bench_warmup_steps=%d%n", WARMUP_STEPS);
        System.out.printf("bench_steps=%d%n", BENCH_STEPS);
        System.out.printf("bench_elapsed_ms=%.6f%n", elapsedMs);
        System.out.printf("bench_speed_cycles_per_s=%.6f%n", speed);

        dut.Finish();
    }
}
