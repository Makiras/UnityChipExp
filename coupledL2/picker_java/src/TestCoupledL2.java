import com.ut.UT_CoupledL2;
import com.xspcomm.WriteMode;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.math.BigInteger;
import java.util.Arrays;
import java.util.Random;
import java.util.random.RandomGenerator;

public class TestCoupledL2 {
    static PrintWriter pwOut = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));
    static UT_CoupledL2 dut;

    static void sendA(int opcode, int size, int address) {
        var valid = dut.master_port_0_0_a_valid;
        var ready = dut.master_port_0_0_a_ready;
        while (!ready.B()) dut.xclock.Step();
        valid.Set(1);
        dut.master_port_0_0_a_bits_opcode.Set(opcode);
        dut.master_port_0_0_a_bits_size.Set(size);
        dut.master_port_0_0_a_bits_address.Set(address);
        dut.xclock.Step();
        valid.Set(0);
    }

    static void getB() {
        var valid = dut.master_port_0_0_b_valid;
        var ready = dut.master_port_0_0_b_ready;
        ready.Set(1);
        while (!valid.B()) dut.xclock.Step();
        ready.Set(0);
    }

    static void sendC(int opcode, int size, int address, long data) {
        var valid = dut.master_port_0_0_c_valid;
        var ready = dut.master_port_0_0_c_ready;

        while (!ready.B()) dut.xclock.Step();
        valid.Set(1);
        dut.master_port_0_0_c_bits_opcode.Set(opcode);
        dut.master_port_0_0_c_bits_size.Set(size);
        dut.master_port_0_0_c_bits_address.Set(address);
        dut.master_port_0_0_c_bits_data.Set(data);
        dut.xclock.Step();
        valid.Set(0);
    }

    static void getD() {
        var valid = dut.master_port_0_0_d_valid;
        var ready = dut.master_port_0_0_d_ready;
        ready.Set(1);
        dut.xclock.Step();
        while (!valid.B()) dut.xclock.Step();
        ready.Set(0);
    }

    static void sendE(int sink) {
        var valid = dut.master_port_0_0_e_valid;
        var ready = dut.master_port_0_0_e_ready;
        while (!ready.B()) dut.xclock.Step();
        valid.Set(1);
        dut.master_port_0_0_e_bits_sink.Set(sink);
        dut.xclock.Step();
        valid.Set(0);
    }

    static void AcquireBlock(int address) {
        sendA(Opcode.A.AcquireBlock.getValue(), 0x6, address);
    }

    static BigInteger GrantData() {
        var opcode = dut.master_port_0_0_d_bits_opcode;
        var data = dut.master_port_0_0_d_bits_data;

        do {
            getD();
        } while (opcode.Get().intValue() != Opcode.D.GrantData.getValue());
        var r_data = data.U64().shiftLeft(64);
        do {
            getD();
        } while (opcode.Get().intValue() != Opcode.D.GrantData.getValue());
        return r_data.or(data.U64());
    }

    static void GrantAck(int sink) {
        sendE(sink);
    }

    static void ReleaseData(int address, BigInteger data) {
        sendC(Opcode.C.ReleaseData.getValue(), 0x6, address, data.longValue());
        sendC(Opcode.C.ReleaseData.getValue(), 0x6, address, data.shiftRight(64).longValue());
    }

    static void ReleaseAck() {
        var opcode = dut.master_port_0_0_d_bits_opcode;
        do {
            getD();
        } while (opcode.Get().intValue() != Opcode.D.ReleaseAck.getValue());
    }

    public static void main(String[] args) throws IOException {
        /* Random Generator */
        var gen_rand = RandomGenerator.getDefault();
        /* DUT init */
        final String[] ARGS = {"+verilator+rand+reset+0"};
        dut = new UT_CoupledL2(ARGS);
        dut.InitClock("clock");
        dut.reset.SetWriteMode(WriteMode.Imme);
        dut.reset.Set(1);
        dut.xclock.Step();
        dut.reset.Set(0);
        for (int i = 0; i < 100; i++) dut.xclock.Step();
        dut.xclock.Step();

        /* Ref */
        BigInteger[] ref_data = new BigInteger[16];
        Arrays.fill(ref_data, BigInteger.ZERO);

        /* Test loop */
        for (int test_loop = 0; test_loop < 4000; test_loop++) {
            var address = gen_rand.nextInt(0xf) << 6;
            var data = new BigInteger(128, Random.from(gen_rand));

            pwOut.print("[CoupledL2 Test%d]: At address(%#03x), ".formatted(test_loop + 1, address));
            /* Read */
            AcquireBlock(address);
            var r_data = GrantData();
            assert (r_data.equals(ref_data[address >> 6]));

            var sink = dut.master_port_0_0_d_bits_sink.Get().intValue();
            GrantAck(sink);


            /* Write */
            ReleaseData(address, data);
            ref_data[address >> 6] = data;
            ReleaseAck();

            pwOut.println("Read: %s, Write: %s".formatted(r_data.toString(), data.toString()));
            pwOut.flush();
        }
    }
}
