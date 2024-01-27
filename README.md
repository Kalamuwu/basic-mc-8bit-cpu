# basic-mc-8bit-cpu

A simple compiler and simulator for an 8-bit computer I decided to build in Minecraft over the course of a few weeks.

At the time, I was learning about very early computing systems, and more advanced circuitry like hardware adders or RAM/ROM.

This repo includes a lookup reference for commands and their function, as well as a handful of sample programs.

### Specs
- 256-byte ROM
- 16 bytes of RAM
- Basic user I/O
- Support for variables and dynamic allocation via the compiler

### Programs
Two files are included for each program;
1. The assembly `.asm` file thrown to the compiler
2. The binary `.bin` file thrown back from the compiler

The binary files would then be read out with something like `hexdump`, and loaded into the ROM via redstone torches. :)
