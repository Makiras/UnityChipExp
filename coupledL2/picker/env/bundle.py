from toffee import Bundle, Signals, Signal

class DecoupledBundle(Bundle):
    ready, valid = Signals(2)

class TileLinkBundleA(DecoupledBundle):
    opcode, param, size, source, address, user_alias, mask, data, corrupt = Signals(9)

class TileLinkBundleB(DecoupledBundle):
    opcode, param, size, source, address, mask, data, corrupt = Signals(8)

class TileLinkBundleC(DecoupledBundle):
    opcode, param, size, source, address, user_alias, data, corrupt = Signals(8)

class TileLinkBundleD(DecoupledBundle):
    opcode, param, size, source, sink, denied, data, corrupt = Signals(8)

class TileLinkBundleE(DecoupledBundle):
    sink = Signal()

class TileLinkBundle(Bundle):
    a = TileLinkBundleA.from_regex(r"a_(?:(valid|ready)|bits_(.*))")
    b = TileLinkBundleB.from_regex(r"b_(?:(valid|ready)|bits_(.*))")
    c = TileLinkBundleC.from_regex(r"c_(?:(valid|ready)|bits_(.*))")
    d = TileLinkBundleD.from_regex(r"d_(?:(valid|ready)|bits_(.*))")
    e = TileLinkBundleE.from_regex(r"e_(?:(valid|ready)|bits_(.*))")
