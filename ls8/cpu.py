"""CPU functionality."""

import sys
import datetime

ADD = 0b10100000
CALL = 80
CMP = 0b10100111
DEC = 0b01100110
HLT = 1
IRET = 19
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110
LDI = 130
MUL = 162
POP = 0b01000110
PRN = 71
PUSH = 0b01000101
RET = 17
ST = 132


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000]*256
        self.reg = [0b00000000]*8
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xf4
        self.im = 5
        self.IS = 6
        self.fl = 0b00000000
        self.running = True
        self.branchtable = {}
        self.branchtable[ADD] = self.handle_add
        self.branchtable[CALL] = self.handle_call
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[DEC] = self.handle_dec
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[POP] = self.handle_pop
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ST] = self.handle_st

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("Usage: python ls8.py examples/mult.ls8")
            sys.exit(1)
        
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0].strip()
                    if num == "":
                        continue
                    value = int(num, 2)
                    self.ram_write(value, address)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "DEC": 
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR
        return

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_ldi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def handle_hlt(self):
        self.running = False

    def handle_add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def handle_dec(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("DEC", operand_a, operand_b)
        self.pc += 3
        
    def handle_mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def handle_push(self):
        operand_a = self.ram_read(self.pc + 1)
        val = self.reg[operand_a]
        self.reg[self.sp] -= 1
        self.ram_write(val, self.reg[self.sp])
        self.pc += 2

    def handle_pop(self):
        operand_a = self.ram_read(self.pc + 1)
        self.reg[operand_a] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.pc += 2

    def handle_call(self):
        ret_loc = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram_write(ret_loc, self.reg[self.sp])
        
        reg = self.ram_read(self.pc + 1)

        sub_rtn_addr = self.reg[reg]

        self.pc = sub_rtn_addr

    def handle_ret(self):
        ret_addr = self.reg[self.sp]
        self.pc = self.ram_read(ret_addr)
        self.reg[self.sp] += 1

    def handle_st(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        val = self.reg[operand_b]
        self.ram_write(val, self.reg[operand_a])

    def handle_cmp(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        if self.reg[operand_a] < self.reg[operand_b]:
            self.fl = 0b00000100
        elif self.reg[operand_a] > self.reg[operand_b]:
            self.fl = 0b00000010
        elif self.reg[operand_a] == self.reg[operand_b]:
            self.fl = 0b00000001
        self.pc += 3

    def handle_jmp(self):
        operand_a = self.ram_read(self.pc + 1)
        self.pc = self.reg[operand_a]

    def handle_jne(self):
        if (self.fl & 0b00000001) == 0:
            self.handle_jmp()
        else:
            self.pc += 2

    def handle_jeq(self):
        if (self.fl & 0b00000001) == 1:
            self.handle_jmp()
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            IR = self.ram_read(self.pc)
            self.branchtable[IR]()




"""
load 10 into R0
Load 20 into R1
Load 19 into R2
CMP R0 R1, should be L
JEQ R2, FL should be 'L', so should fail. Instead, it hangs

01010101
"""