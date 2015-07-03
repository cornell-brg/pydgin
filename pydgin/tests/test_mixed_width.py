"""
This is a cut down (2-instruction) version of the Epiphany simulator,
used to test the mixed 16- and 32-bit instruction set.
"""

from pydgin.debug import Debug
from pydgin.misc import create_risc_decoder
from pydgin.sim import Sim, init_sim
from pydgin.storage import Memory, RegisterFile

reg_map = { 'pc' : 0, 'STATUS' : 1 }

encodings = [
    ['nop16',   'xxxxxx01' '10100010'],
    ['hello32', '11111111' '11111111' '11111111' '11111111'],
    ['halt16',  'xxxxxx01' '11000010'],
]


def execute_nop16(s, inst):
    """Do nothing but increment the PC.
    16 bit instruction.
    """
    s.pc += 2


def execute_hello32(s, inst):
    """Print Hello, world!.
    32 bit instruction.
    """
    print '\nHello, world!'
    s.pc += 4


def execute_halt16(s, inst):
    """Set a flag in the STATUS register and HALT the machine.
    16 bit instruction.
    """
    s.rf[reg_map['STATUS']] |= 1
    s.pc += 2
    s.running = False


decode = create_risc_decoder(encodings, globals(), debug=True)


class ExampleState(object):

    def __init__(self, memory, debug):
        self.pc        = 2  # Would be 0 but storage inserts an extra 2 bytes.
        self.mem       = memory
        self.debug     = debug
        self.rf        = RegisterFile(constant_zero=False, num_regs=2)
        self.running   = True   # Set False by halt16 instruction.
        self.debug     = debug
        self.rf.debug  = debug
        self.mem.debug = debug
        self.status    = 0
        self.num_insts = 0
        self.stats_en  = True
        self.stat_num_insts = 0

    def fetch_pc(self):
        return self.pc


class ExampleInstruction(object):

    def __init__(self, bits, str):
        self.bits = bits
        self.str  = str


class SingleWidthMachine(Sim):

    def __init__(self):
        Sim.__init__(self, "Example", inst_sizes=[16], jit_enabled=True) # Breaks if False.

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return ExampleInstruction(bits, inst_str), exec_fun


    def load_program(self, instructions, **args):
        """Load the program into a memory object.
        Instructions should take the form of a list of tuples containing an
        instruction and its width. e.g.:
            [ (0b0, 32) ]
        """
        mem = Memory(size=2**18, byte_storage=True)
        written_so_far = 0
        for data, width in instructions:
            num_bytes = width / 8
            mem.write(written_so_far, num_bytes, data)
            written_so_far += num_bytes
        self.state = ExampleState(mem, Debug(flags=['insts', 'mem', 'rf', 'regdump']))


class MixedWidthMachine(Sim):

    def __init__(self):
        Sim.__init__(self, "Example", inst_sizes=[32, 16], jit_enabled=True) # Breaks if False.

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return ExampleInstruction(bits, inst_str), exec_fun


    def load_program(self, instructions, **args):
        """Load the program into a memory object.
        Instructions should take the form of a list of tuples containing an
        instruction and its width. e.g.:
            [ (0b0, 32) ]
        """
        mem = Memory(size=2**18, byte_storage=True)
        written_so_far = 0
        for data, width in instructions:
            num_bytes = width / 8
            mem.write(written_so_far, num_bytes, data)
            written_so_far += num_bytes
        self.state = ExampleState(mem, Debug(flags=['insts', 'mem', 'rf', 'regdump']))

init_sim(SingleWidthMachine())
init_sim(MixedWidthMachine())


def test_only16bit_instructions():
    """This test case has been transcribed directly from an ELF file.
    """
    instructions = [(0b0000000110100010, 16),                  # nop16
                    (0b0000000111000010, 16),                  # halt16
                    ]
    machine = SingleWidthMachine()
    machine.load_program(instructions)
    machine.run()
    # nop16 increments by 2, halt16 increments by 2.
    assert machine.state.pc == 4, "Expected pc = 4, got pc = {0}".format(machine.state.pc)
    assert not machine.state.running, "Machine not HALTed."

def test_mixed_width_instructions():
    instructions = [(0b0000000110100010, 16),                  # nop16
                    (0b11111111111111111111111111111111, 32),  # hello32
                    (0b0000000111000010, 16),                  # halt16
                    ]
    machine2 = MixedWidthMachine()
    machine2.load_program(instructions)
    machine2.run()
    # nop16 increments by 2, hello32 increments by 4, halt16 increments by 2.
    assert machine2.state.pc == 8, "Expected pc = 8, got pc = {0}".format(machine2.state.pc)
    assert not machine2.state.running, "Machine not HALTed."
