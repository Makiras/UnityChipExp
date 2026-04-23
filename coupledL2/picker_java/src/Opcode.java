public class Opcode {
    public enum A {
        PutFullData(0x0),
        PutPartialData(0x1),
        ArithmeticData(0x2),
        LogicalData(0x3),
        Get(0x4),
        Hint(0x5),
        AcquireBlock(0x6),
        AcquirePerm(0x7);

        private final int value;

        A(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }

    public enum B {
        ProbeBlock(0x6), ProbePerm(0x7);

        private final int value;

        B(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }

    public enum C {
        ProbeAck(0x4), ProbeAckData(0x5), Release(0x6), ReleaseData(0x7);

        private final int value;

        C(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }

    public enum D {
        AccessAck(0x0), AccessAckData(0x1), HintAck(0x2), Grant(0x4), GrantData(0x5), ReleaseAck(0x6);

        private final int value;

        D(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }

    public enum E {
        GrantAck(0x4);

        private final int value;

        E(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }
}
