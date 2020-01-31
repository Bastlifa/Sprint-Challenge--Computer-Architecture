"""CPU functionality."""

import sys
import datetime

HLT = 1
RET = 17
IRET = 19
PUSH = 69
POP = 70
PRN = 71
CALL = 80
JMP = 84
JEQ = 85
JNE = 86
DEC = 102
NOT = 105
LDI = 130
ST = 132
ADD = 160
MUL = 162
MOD = 164
CMP = 167
AND = 168
OR = 170
XOR = 171
SHL = 172
SHR = 173
ADDI = 200



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
        self.maskedInterrupts = 0 # non_pythonic casing
        self.IS = 6
        self.fl = 0b00000000
        self.running = True
        self.branchtable = {}
        self.branchtable[ADD] = self.handle_add
        self.branchtable[ADDI] = self.handle_addi
        self.branchtable[AND] = self.handle_and
        self.branchtable[CALL] = self.handle_call
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[DEC] = self.handle_dec
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[MOD] = self.handle_mod
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[NOT] = self.handle_not
        self.branchtable[OR] = self.handle_or
        self.branchtable[POP] = self.handle_pop
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[RET] = self.handle_ret
        self.branchtable[SHL] = self.handle_shl
        self.branchtable[SHR] = self.handle_shr
        self.branchtable[ST] = self.handle_st
        self.branchtable[XOR] = self.handle_xor

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

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "DEC": 
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            self.reg[reg_a] = (a | b) & ~(a & b)
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "ADDI":
            self.reg[reg_a] += reg_b
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

    def handle_and(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("AND", operand_a, operand_b)
        self.pc += 3

    def handle_or(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("OR", operand_a, operand_b)
        self.pc += 3

    def handle_xor(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("XOR", operand_a, operand_b)
        self.pc += 3

    def handle_not(self):
        operand_a = self.ram_read(self.pc + 1)
        self.alu("NOT", operand_a)
        self.pc += 2

    def handle_shl(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("SHL", operand_a, operand_b)
        self.pc += 3

    def handle_shr(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("SHR", operand_a, operand_b)
        self.pc += 3

    def handle_mod(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MOD", operand_a, operand_b)
        self.pc += 3

    def handle_addi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADDI", operand_a, operand_b)
        self.pc += 3


    def run(self):
        """Run the CPU."""
        self.running = True
        t = datetime.datetime.now()
        while self.running:
            if datetime.datetime.now() - t < datetime.timedelta(seconds=1):
                # do the interrupt
                # set bit 0 of r6. Set to what? 1?
                self.IS = 0b00000001
                

                t = datetime.datetime.now()
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