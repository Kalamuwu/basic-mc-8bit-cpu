#!/usr/bin/env python

# test.py
# simulates in-game computer and runs compiled binary programs

import argparse
parser = argparse.ArgumentParser(
    description="Simulates the in-game computer and runs compiled binary programs."
)
parser.add_argument("file", help="Compiled binary file to run on the simulated computer")
parser.add_argument("-d", "--debug", help="Show running output per step", action="store_true")
parser.add_argument("-w", "--skip-rom-size-check", help="Do not fail if the given binary is larger than the actual system ROM. " + \
                                                        "Run it as if system ROM were large enough to hold it.", action="store_true")
args = parser.parse_args()


import sys
import typing
import random
def phex(i: int) -> str:
    return ('0' if i<16 else '') + hex(i)[2:].upper()
def pbin(i: int) -> str:
    binlen = len(bin(i))-2
    return '0'*(8-binlen) + bin(i)[2:]

class Computer:    
    def __init__(self, operations: typing.List[typing.Callable]):
        self.__rom = []
        self.__ram = [0x0 for _ in range(16)]
        self.operations = operations
        self.halted = True
        self.__line = 0x00
        self.__register = 0x00
    
    @property
    def line(self): return self.__line
    @line.setter
    def line(self, addr):
        self.__line = addr % len(self.__rom)
    @property
    def register(self): return self.__register
    @register.setter
    def register(self, data): self.__register = data & 0xFF
    
    def write(self, addr: int, data: int) -> None:
        """ write value to ram, trimmed to 4- and 8-bit respective sizes """
        self.__ram[addr & 0xF] = data & 0xFF
    
    def read(self, addr: int) -> int:
        """ return value from ram, trimmed to 4- and 8-bit respective sizes """
        return self.__ram[addr & 0xF] & 0xFF
    
    def give_me_next_line(self):
        self.line += 1
        return self.__rom[self.line]
    
    def show_ram(self):
        print("  addr | hex   bin")
        for addr,byte in enumerate(self.__ram[:-2]):
            print(f"    {phex(addr)} | {phex(byte)}    {pbin(byte)} ")
        print(f"    rr | {phex(self.register)}    {pbin(self.register)}")
    
    def run_rom(self, rom: typing.List[int], debug=False) -> typing.List[int]:
        """ Steps through the given binary rom. Returns the state of the RAM upon halt. """
        self.halted = False
        self.__rom = rom
        while not self.halted:
            l = self.line
            instr = self.__rom[self.line]
            cmd = (instr & 0xF0) >> 4
            dat =  instr & 0x0F
            self.operations[cmd](self, dat, debug=debug)
            if debug:
                self.show_ram()
                print(f"\nline {phex(l)}: ")
                print(f" executed:  {self.operations[cmd].__name__[1:]} {phex(dat)[1:]} ")
                print('\n')
                input()
            self.line += 1
        return self.__ram

if __name__ == '__main__':
    def _nop(computer: Computer, dat: int, debug=False):
        """ no operation """
    def _hlt(computer: Computer, dat: int, debug=False):
        """ halt program clock """
        computer.halted = True
    def _sto(computer: Computer, dat: int, debug=False):
        """ set &reg <-- &dat if dat != &OUTPUT; else set &reg <-- rand[0x00, 0xFF] """
        if dat == 0xE:
            computer.register = int(input("input 8-bit number >")) & 0xFF
        elif dat == 0xF:
            computer.register = random.randint(0x00, 0xFF)
        else:
            computer.register = computer.read(dat)
    def _pop(computer: Computer, dat: int, debug=False):
        """ set &dat <-- &reg """
        if dat == 0xF:
            print(computer.register)
        else:
            computer.write(dat, computer.register)
    def _set(computer: Computer, dat: int, debug=False):
        """ set &dat <-- data2 if dat != &INPUT; else set &reg <-- data2 """
        val = computer.give_me_next_line()
        if debug: print("loaded: ", val)
        if dat == 0xE:
            computer.register = val
        else:
            computer.write(dat, val)
    def _add(computer: Computer, dat: int, debug=False):
        """ set &reg <-- [ &reg + &dat ] """
        computer.register = (computer.register + computer.read(dat))
    def _jmp(computer: Computer, dat: int, debug=False):
        """ jump to line number data2 """
        val = computer.give_me_next_line()
        if debug: print("jumping to: ", val)
        computer.line = val-1
    def _jmc(computer: Computer, dat: int, debug=False):
        """ jump to line number data2 if &reg == 0xFF """
        val = computer.give_me_next_line()
        if computer.register == 0xFF:
            if debug: print("jumping to: ", val)
            computer.line = val-1
    def _neg(computer: Computer, dat: int, debug=False):
        """ set &dat <-- ( NOT &dat ) + 0x1 """
        computer.write(dat, (~dat + 1))
    def _rgt(computer: Computer, dat: int, debug=False):
        """ set &reg == 0xFF if (&reg > &dat) else 0x00 """
        computer.register = 0xFF if computer.register > computer.read(dat) else 0x00
    def _rlt(computer: Computer, dat: int, debug=False):
        """ set &reg == 0xFF if (&reg < &dat) else 0x00 """
        computer.register = 0xFF if computer.register < computer.read(dat) else 0x00
    def _req(computer: Computer, dat: int, debug=False):
        """ set &reg == 0xFF if (&reg == &dat) else 0x00 """
        computer.register = 0xFF if computer.register == computer.read(dat) else 0x00
    def _not(computer: Computer, dat: int, debug=False):
        """ set &reg <-- ~&reg """
        computer.register = (~computer.register)
    def _and(computer: Computer, dat: int, debug=False):
        """ set &reg <-- [ &reg AND &dat ] """
        computer.register = (computer.register & computer.read(dat))
    def _xor(computer: Computer, dat: int, debug=False):
        """ set &reg <-- [ &reg XOR &dat ] """
        computer.register = (computer.register ^ computer.read(dat))
    def _orr(computer: Computer, dat: int, debug=False):
        """ set &reg <-- [ &reg OR  &dat ] """
        computer.register = (computer.regiter | computer.read(dat))
    
    computer = Computer([_nop, _hlt, _sto, _pop, _set, _add, _jmp, _jmc,
                         _neg, _rgt, _rlt, _req, _not, _and, _xor, _orr])
    
    with open(args.file, 'rb') as binaryfile:
        binary = list(bytearray(binaryfile.read()))
    MAX_ROM = 0x7F
    if args.skip_rom_size_check:
        MAX_ROM = max(len(binary), MAX_ROM)
    else:
        if len(binary) > MAX_ROM:
            raise IOError(f"System does not have enough ROM to hold this program! Length: {len(binary)}  available: {MAX_ROM}")
    binary.extend([0x00 for _ in range(MAX_ROM+1 - len(binary))])  # pad end with 0x00's
    
    if args.debug:
        print("Loaded ROM:\n")
        for i in range(8):
            row = binary[16*i : 16*(i+1)]
            print("   ", *[phex(r) for r in row])
        print('\n')
    
    computer.run_rom(list(binary), debug=bool(args.debug))