#include "UT_CoupledL2.hpp"
using TLDataArray = std::array<uint64_t, 2>;

enum class OpcodeA : uint32_t {
  PutFullData = 0x0,
  PutPartialData = 0x1,
  ArithmeticData = 0x2,
  LogicalData = 0x3,
  Get = 0x4,
  Hint = 0x5,
  AcquireBlock = 0x6,
  AcquirePerm = 0x7,
};

enum class OpcodeB : uint32_t { ProbeBlock = 0x6, ProbePerm = 0x7 };

enum class OpcodeC : uint32_t { ProbeAck = 0x4, ProbeAckData = 0x5, Release = 0x6, ReleaseData = 0x7 };

enum class OpcodeD : uint32_t { AccessAck, AccessAckData, HintAck, Grant = 0x4, GrantData = 0x5, ReleaseAck = 0x6 };

enum class OpcodeE : uint32_t { GrantAck = 0x4 };

constexpr std::initializer_list<const char *> ARGS = {"+verilator+rand+reset+0"};
auto dut = UTCoupledL2(ARGS);
auto &clk = dut.xclock;

void sendA(OpcodeA opcode, uint32_t size, uint32_t address) {
  const auto &valid = dut.master_port_0_0_a_valid;
  const auto &ready = dut.master_port_0_0_a_ready;
  while (ready.value == 0x0) clk.Step();
  valid.value = 1;
  dut.master_port_0_0_a_bits_opcode.value = opcode;
  dut.master_port_0_0_a_bits_size.value = size;
  dut.master_port_0_0_a_bits_address.value = address;
  clk.Step();
  valid.value = 0;
}

void getB() {
  assert(false);
  const auto &valid = dut.master_port_0_0_b_valid;
  const auto &ready = dut.master_port_0_0_b_ready;
  ready.value = 1;
  while (valid.value == 0)
    clk.Step();
  dut.master_port_0_0_b_bits_opcode = 0x0;
  dut.master_port_0_0_b_bits_param = 0x0;
  dut.master_port_0_0_b_bits_size = 0x0;
  dut.master_port_0_0_b_bits_source = 0x0;
  dut.master_port_0_0_b_bits_address = 0x0;
  dut.master_port_0_0_b_bits_mask = 0x0;
  dut.master_port_0_0_b_bits_data = 0x0;
  dut.master_port_0_0_b_bits_corrupt = 0x0;
  clk.Step();
  ready.value = 0;
}

void sendC(OpcodeC opcode, uint32_t size, uint32_t address, uint64_t data) {
  const auto &valid = dut.master_port_0_0_c_valid;
  const auto &ready = dut.master_port_0_0_c_ready;

  while (ready.value == 0) clk.Step();
  valid.value = 1;
  dut.master_port_0_0_c_bits_opcode.value = opcode;
  dut.master_port_0_0_c_bits_size.value = size;
  dut.master_port_0_0_c_bits_address.value = address;
  dut.master_port_0_0_c_bits_data.value = data;
  clk.Step();
  valid.value = 0;
}

void getD() {
  const auto &valid = dut.master_port_0_0_d_valid;
  const auto &ready = dut.master_port_0_0_d_ready;
  ready.value = 1;
  clk.Step();
  while (valid.value == 0) clk.Step();
  ready.value = 0;
}

void sendE(uint32_t sink) {
  const auto &valid = dut.master_port_0_0_e_valid;
  const auto &ready = dut.master_port_0_0_e_ready;
  while (ready.value == 0) clk.Step();
  valid.value = 1;
  dut.master_port_0_0_e_bits_sink.value = sink;
  clk.Step();
  valid.value = 0;
}

void AcquireBlock(uint32_t address) { sendA(OpcodeA::AcquireBlock, 0x6, address); }

void GrantData(TLDataArray &r_data) {
  const auto &opcode = dut.master_port_0_0_d_bits_opcode;
  const auto &data = dut.master_port_0_0_d_bits_data;

  for (int i = 0; i < 2; i++) {
    do { getD(); } while (opcode.value != OpcodeD::GrantData);
    r_data[i] = data.value;
  }
}

void GrantAck(uint32_t sink) { sendE(sink); }

void ReleaseData(uint32_t address, const TLDataArray &data) {
  for (int i = 0; i < 2; i++)
    sendC(OpcodeC::ReleaseData, 0x6, address, data[i]);
}

void ReleaseAck() {
  const auto &opcode = dut.master_port_0_0_d_bits_opcode;
  do { getD(); } while (opcode.value != OpcodeD::ReleaseAck);
}

int main() {
  TLDataArray ref_data[16] = {};
  /* Random generator */
  std::random_device rd;
  std::mt19937_64 gen_rand(rd());
  std::uniform_int_distribution<uint32_t> distrib(0, 0xf - 1);

  /* DUT init */
  dut.InitClock("clock");
  dut.reset.SetWriteMode(xspcomm::WriteMode::Imme);
  dut.reset.value = 1;
  clk.Step();
  dut.reset.value = 0;
  for (int i = 0; i < 100; i++) clk.Step();

  /* Test loop */
  for (int test_loop = 0; test_loop < 4000; test_loop++) {
    uint32_t d_sink;
    TLDataArray data{}, r_data{};
    /* Generate random */
    const auto address = distrib(gen_rand) << 6;
    for (auto &i : data)
      i = gen_rand();

    printf("[CoupledL2 Test\t%d]: At address(0x%03x), ", test_loop + 1, address);
    /* Read */
    AcquireBlock(address);
    GrantData(r_data);

    // Print read result
    printf("Read: ");
    for (const auto &x : r_data)
      printf("%08lx", x);

    d_sink = dut.master_port_0_0_d_bits_sink.value;
    assert ((r_data == ref_data[address >> 6]) && "Read Failed");
    GrantAck(d_sink);

    /* Write */
    ReleaseData(address, data);
    ref_data[address >> 6] = data;
    ReleaseAck();

    // Print write data
    printf(", Write: ");
    for (const auto &x : data)
      printf("%08lx", x);
    printf(".\n");
  }

  return 0;
}
