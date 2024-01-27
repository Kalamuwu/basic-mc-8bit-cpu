cmt program: number_guessing_game.asm
cmt number guessing game with currency and randomizer

cmt 100
def &cash
set &cash 0x64

cmt -10
def &amtToLose
set &amtToLose 0xF6

cmt 50
def &amtToWin
set &amtToWin 0x32

def &rand
def &zero

cmt get user input and check
lbl .input
rnd
pop &rand
neg &rand
sto &INPUT
jmc .end
req &rand
jmc .correct
jmp .wrong

lbl .correct
cmt flash on and off, twice
set &OUTPUT 0x00
set &OUTPUT 0xFF
set &OUTPUT 0x00
set &OUTPUT 0xFF
set &OUTPUT 0x00
sto &cash
add &amtToWin
pop &OUTPUT
pop &cash
jmp .input

lbl .wrong
cmt flash alternating, twice
set &OUTPUT 0xAA
set &OUTPUT 0x55
set &OUTPUT 0xAA
set &OUTPUT 0x55
set &OUTPUT 0x00
sto &cash
add &amtToLose
pop &OUTPUT
pop &cash
req &zero
jmc .end
jmp .input

lbl .end
sto &cash
pop &OUTPUT
hlt