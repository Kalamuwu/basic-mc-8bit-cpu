cmt program: fib.asm
cmt steps through the fibonacci sequence

cmt set up variables
def &a
def &b
set &b 0x01

lbl .head

cmt sequence pt.1
sto &a
add &b
pop &a
pop &OUTPUT

cmt sequence pt.2
sto &b
add &a
pop &b
pop &OUTPUT

jmp .head