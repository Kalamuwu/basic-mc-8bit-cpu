#!/usr/bin/env python

# compile.py
# compiles input file to binary data

import argparse
parser = argparse.ArgumentParser(
    description="Compiles the given assembly file into a binary, ready for executing on the real machine or simulated one."
)
parser.add_argument("infile", help="Assembly file to link and compile")
parser.add_argument("-o", "--outfile", help="Name of compiled binary file. Defaults to '<infile>.bin'.")
parser.add_argument("-w", "--skip-rom-size-check", help="Do not fail if the compiled binary is larger than the actual system ROM.", action="store_true")
args = parser.parse_args()

import sys
import typing

## constants -- machine specs

USABLE_RAM_SIZE = 16
""" Bytes of RAM present in the system (including special symbols)"""

SYSTEM_RAM_NAME_ADDR = {
    0b1110: "INPUT",
    0b1111: "OUTPUT"
}
""" Special system-reserved memory addresses to disallow reserving variables to, like I/O addresses """

USABLE_ROM_SIZE = 256
""" Number of ROM lines available for programming """



class SpecException(Exception):
    """ Thrown when an error occurs relating to asking too much of the system. """
class LogicError(SyntaxError):
    """ Thrown when something will technically compile but won't run, like writing to a read-only input memory address. """

class SystemVariables:
    def __init__(self):
        self.__allocated = [None for _ in range(USABLE_RAM_SIZE)]
        self.__jumps = {}
        for addr,name in SYSTEM_RAM_NAME_ADDR.items():
            self.__allocated[addr] = name
    
    def alloc_var(self, name: str) -> int:
        """ Gives a name to a memory address; checks internal variables and makes sure the computer has enough space. """
        if not name.isalnum():
            raise SyntaxError(f"Expected variable declaration, got '{name}'. Variable names must be alphanumeric with no whitespace characters.")
        if name in self.__allocated:
            raise SyntaxError(f"Variable with name '{name}' already defined")
        for addr,varname in enumerate(self.__allocated):
            if varname is None:
                self.__allocated[addr] = name
                return addr
        raise SpecException(f"No memory available - Ran out of usable RAM space trying to allocate new variable {name}")
    
    def add_label(self, name: str, line: int) -> None:
        """ Gives a name to a line number. """
        if not name.isalnum():
            raise SyntaxError(f"Expected jump label declaration, got '{name}'. Jump label names must be alphanumeric with no whitespace characters.")
        if name in self.__jumps:
            raise SyntaxError(f"Jump label with name '{name}' already defined")
        self.__jumps[name] = line

    def get_var(self, name: str) -> int:
        """ Returns the memory address of the given variable. """
        for addr,varname in enumerate(self.__allocated):
            if name == varname:
                return addr
        raise SyntaxError(f"Variable with name '{name}' not found")

    def get_lbl(self, name: str) -> int:
        """ Returns the line number associated with the given label. """
        for label,linenum in self.__jumps.items():
            if name == label:
                return linenum
        raise SyntaxError(f"Jump label with name '{name}' not found")
    
    def free(self, name: str) -> int:
        """ Frees the variable of the given name. This allows the same address to be used under a different name. """
        # check special names
        if name in SYSTEM_RAM_NAME_ADDR.values():
            raise LogicError("Cannot free special addresses!")
        # check allocated variables
        for addr,varname in self.__allocated:
            if name == varname:
                self.__allocated[addr] = None
                return addr
        # loop did not exit, so name was not found. raise error
        raise SyntaxError(f"variable with name '{name}' not found")
    
    def eval_data(self, data: str) -> int:
        """ Evaluate the incoming data as a variable, a label, or a literal. """
        if data.startswith('&'):
            return self.get_var(data[1:])
        try:
            return int(data, base=0)
        except:
            raise SyntaxError(f"Could not parse variable or value '{data}'")
    
    def dump(self):
        alloc_strings = []
        for addr,name in enumerate(self.__allocated):
            alloc_strings.append(f"{hex(addr)} {name}")
        return "Allocated memory:  " + " | ".join(alloc_strings) + \
               "\nRegistered labels:  " + " ".join(self.__jumps) if len(self.__jumps) else "None"


def parse_program(program: typing.List[str]) -> typing.List[int]:
    VERB_COMMANDS = ["nop", "hlt", "sto", "pop", "set", "add", "jmp", "jmc", "neg", "rgt", "rlt", "req", "not", "and", "xor", "orr"]
    CMPL_COMMANDS = ["def", "fre", "lbl", "cmt", "rnd"]  # compiler-only commands
    variables_registry = SystemVariables()
    
    output = []
    for linenum,line in enumerate(program):
        try:
            line = line.split()
            if len(line) == 0 or line[0] in ["cmt"]: continue
            
            verb = line[0]
            if verb not in VERB_COMMANDS and verb not in CMPL_COMMANDS:
                raise SyntaxError(f"verb {verb} not found")
            
            if verb in ["nop", "hlt", "not", "rnd"]:
                if len(line) > 1: print(f"SyntaxWarning extra data '{' '.join(line[1:])}' on line {linenum+1} ignored")
                if verb == "rnd":
                    output.append(0x2E)  # 'rnd' is an alias to 'sto &INPUT'
                else:
                    output.append(VERB_COMMANDS.index(verb) << 4)
                continue
            
            if len(line) < 2: raise SyntaxError(f"Incomplete data for verb {verb} on line {linenum+1}")
            data = line[1]
            if verb == "def":
                if not data.startswith('&'): raise SyntaxError(f"Expected variable declaration, got '{data}'")
                variables_registry.alloc_var(data[1:])
                continue
            if verb == "fre":
                if not data.startswith('&'): raise SyntaxError(f"Expected variable declaration, got '{data}'")
                variables_registry.free(data[1:])
                continue
            if verb == "lbl":
                if not data.startswith('.'): raise SyntaxError(f"Expected jump label declaration, got '{data}'")
                variables_registry.add_label(data[1:], len(output))
                continue
            
            if verb in ["jmp", "jmc"]:
                if len(line) > 2: print(f"SyntaxWarning extra data '{' '.join(line[2:])}' on line {linenum+1} ignored")
                output.append(VERB_COMMANDS.index(verb) << 4)
                output.append(line[1])
                continue
            data = variables_registry.eval_data(data)
            if verb in ["sto", "pop", "add", "neg", "rgt", "rlt", "req", "and", "xor", "orr"]:
                if len(line) > 2: print(f"SyntaxWarning extra data '{' '.join(line[2:])}' on line {linenum+1} ignored")
                output.append((VERB_COMMANDS.index(verb) << 4) | data)
                continue
            if len(line) < 3: raise SyntaxError(f"Incomplete data for verb {verb} on line {linenum+1}")
            data2 = variables_registry.eval_data(line[2])
            if verb == "set":
                if len(line) > 3: print(f"SyntaxWarning extra data '{' '.join(line[3:])}' on line {linenum+1} ignored")
                output.append(VERB_COMMANDS.index(verb) << 4 | data)
                output.append(data2)
                continue
            
            raise SyntaxError(f"Verb {verb} not implemented. this error should not appear.")
        
        except Exception as e:
            print(e, f"on line {linenum+1}: {' '.join(line)}")
            print("System dump:", variables_registry.dump())
            raise
    
    # finish filling jump labels
    for i,line in enumerate(output):
        if type(line) == str:
            output[i] = variables_registry.get_lbl(line[1:])
    
    return output


if __name__ == '__main__':
    with open(args.infile, 'r') as asmfile:
        assembly = asmfile.readlines()
    
    binary = parse_program(assembly)
    if len(binary) > USABLE_ROM_SIZE and not args.w:
        raise SpecException(f"No program space available - Ran out of usable ROM space. Usable ROM" +
                            f" is {USABLE_RAM_SIZE} bytes, and compiled binary is {len(binary)}.")
    
    if args.outfile is None:
        if args.infile.endswith(".asm"):  # remove .asm ending if present
            args.infile = args.infile[:-4]
        args.outfile = args.infile + '.bin'
    
    with open(args.outfile, 'wb') as binfile:
        binfile.write(bytes(binary))
    
    print("Done. No errors reported.")
    print(f"Compiled size: {len(binary)} bytes")
