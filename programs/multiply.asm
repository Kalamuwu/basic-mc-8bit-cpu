cmt program: multiply.asm
cmt inputs numbers a and b, and outputs a * b

cmt set up variables
def &addend
def &accum
def &repeat
def &negone
def &zero

cmt load numbers
set &negone 0xFF
sto &INPUT
pop &addend
pop &accum
sto &INPUT
pop &repeat

cmt add: the jump point which will accumulate the multiplication
lbl .add
sto &repeat
add &negone
pop &repeat
req &zero
jmc .tail
sto &accum
add &addend
pop &accum
jmp .add

cmt tail: jump point to output and exit
lbl .tail
sto &accum
pop &OUTPUT
hlt
