import math

# Function to sign-extend a 12-bit immediate value
# Ronald Chen
def sign_extend_12(value):
    # Check if the sign bit is set
    if value & (1 << 11):
        # If set, extend with 1s
        return (value & 0x7FF) - 0x800
    else:
        # Otherwise, extend with 0s
        return value & 0x7FF

# Function to sign-extend a 13-bit immediate value
def sign_extend_13(value):
    # Check if the sign bit is set
    if value & (1 << 12):
        # If set, extend with 1s
        return (value & 0x1FFF) - 0x2000
    else:
        # Otherwise, extend with 0s
        return value & 0x1FFF

# Function to decode R-type instruction
def decode_R(instr, opcode):
    rd = (instr >> 7) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    funct7 = (instr >> 25) & 0x7F
         # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, rs1, rs2, "NA", funct3, funct7

# Function to decode I-type instruction
def decode_I(instr):
    rd = (instr >> 7) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12((instr >> 20) & 0x5F) # Sign extend immediate
    funct3 = (instr >> 12) & 0b111
         # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, rs1, "NA", imm, funct3, "NA"

# Function to decode S-type instruction
def decode_S(instr):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12(((instr >> 25) << 5) | ((instr >> 7) & 0x1F)) # Sign extend immediate
    funct3 = (instr >> 12) & 0b111
         # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, "NA", rs1, rs2, imm, funct3, "NA"

# Function to decode SB-type instruction
def decode_SB(instr, opcode):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    imm = sign_extend_13(((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) |
                         (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)) # Sign extend immediate
         # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, "NA", rs1, rs2, imm, funct3, "NA"

# Function to decode UJ-type instruction
def decode_UJ(instr):
    rd = (instr >> 7) & 0x1F
    opcode = instr & 0x7F
    imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) | \
          (((instr >> 20) & 0x1) << 11) | (((instr >> 21) & 0x3FF) << 1)
         # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, "NA", "NA", imm, "NA", "NA"


def decoder(binary):
    instr = 0
    binary = str(binary)
    # print(binary)
    for i, bit in enumerate(binary):
        if bit == '1':
            instr |= (1 << (31 - i))

    opcode = instr & 0x7F
    if opcode == 0b0110011: # R-type
        return decode_R(instr, opcode)
    elif opcode == 0b0000011 or opcode == 0b0010011 or opcode == 0b1100111: # I-type
        return decode_I(instr)
    elif opcode == 0b0100011: # S-type
        return decode_S(instr)
    elif opcode == 0b1100011: # SB-type
        return decode_SB(instr, opcode)
    elif opcode == 0b1101111: # UJ-type
        return decode_UJ(instr)