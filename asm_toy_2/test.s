

# Move src value into register
mfc0 r1, mngr2proc < 4278255360


# Instruction under test
xori r3, r1, 3855


# Check the result
mtc0 r3, proc2mngr > 4278251535



# Move src value into register
mfc0 r1, mngr2proc < 267390960


# Instruction under test
xori r3, r1, 61680


# Check the result
mtc0 r3, proc2mngr > 267452160



# Move src value into register
mfc0 r1, mngr2proc < 16711935


# Instruction under test
xori r3, r1, 3855


# Check the result
mtc0 r3, proc2mngr > 16715760



# Move src value into register
mfc0 r1, mngr2proc < 4027576335


# Instruction under test
xori r3, r1, 61680


# Check the result
mtc0 r3, proc2mngr > 4027515135


