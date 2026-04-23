from toffee import Agent, driver_method
from toffee.triggers import Value
from bundle import TileLinkBundle


class TilelinkOPCodes:
    class A:
        PutFullData = 0x0
        PutPartialData = 0x1
        ArithmeticData = 0x2
        LogicalData = 0x3
        Get = 0x4
        Hint = 0x5
        AcquireBlock = 0x6
        AcquirePerm = 0x7

    class B:
        Probe = 0x8

    class C:
        ProbeAck = 0x4
        ProbeAckData = 0x5
        Release = 0x6
        ReleaseData = 0x7

    class D:
        AccessAck = 0x0
        AccessAckData = 0x1
        HintAck = 0x2
        Grant = 0x4
        GrantData = 0x5
        ReleaseAck = 0x6

    class E:
        GrantAck = 0x4


class TileLinkAgent(Agent):
    def __init__(self, tlbundle: TileLinkBundle):
        super().__init__(tlbundle.step)

        self.tlbundle = tlbundle

    @driver_method()
    async def put_a(self, dict):
        dict["valid"] = 1
        self.tlbundle.a.assign(dict)
        await Value(self.tlbundle.a.ready, 1)
        self.tlbundle.a.valid.value = 0

    @driver_method()
    async def get_d(self):
        self.tlbundle.d.ready.value = 1
        await Value(self.tlbundle.d.valid, 1)
        result = self.tlbundle.d.as_dict()
        self.tlbundle.d.ready.value = 0
        return result

    @driver_method()
    async def get_b(self):
        self.tlbundle.b.ready.value = 1
        await Value(self.tlbundle.b.valid, 1)
        result = self.tlbundle.b.as_dict()
        self.tlbundle.b.ready.value = 0
        return result

    @driver_method()
    async def put_c(self, dict):
        dict["valid"] = 1
        self.tlbundle.c.assign(dict)
        await Value(self.tlbundle.c.ready, 1)
        self.tlbundle.c.valid.value = 0

    @driver_method()
    async def put_e(self, dict):
        dict["valid"] = 1
        self.tlbundle.e.assign(dict)
        await Value(self.tlbundle.e.ready, 1)
        self.tlbundle.e.valid.value = 0

    ################################

    async def aquire_block(self, address):
        await self.put_a(
            {
                "*": 0,
                "size": 0x6,
                "opcode": TilelinkOPCodes.A.AcquireBlock,
                "address": address,
            }
        )

        data = 0x0
        for i in range(2):
            ret = await self.get_d()
            while ret["opcode"] != TilelinkOPCodes.D.GrantData:
                ret = await self.get_d()
            data = (ret["data"] << (256 * i)) | data

        await self.put_e({"sink": ret["sink"]})

        return data

    async def release_data(self, address, data):
        for _ in range(2):
            await self.put_c(
                {
                    "*": 0,
                    "size": 0x6,
                    "opcode": TilelinkOPCodes.C.ReleaseData,
                    "address": address,
                    "data": data % (2**256),
                }
            )
            data = data >> 256

        x = await self.get_d()
        while x["opcode"] != TilelinkOPCodes.D.ReleaseAck:
            x = await self.get_d()
