cmt program: cumsum.asm
cmt calculates the cumulitive sum of all numbers fed to it

cmt set up variables
def &sum
def &inp
def &zero

cmt input and add a number
lbl .add
sto &INPUT
pop &inp
req &zero
jmc .tail
sto &sum
add &inp
pop &sum
jmp .add

cmt tail: jump point to output and exit
lbl .tail
sto &sum
pop &OUTPUT
hlt