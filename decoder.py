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
# Ronald Chen
def sign_extend_13(value):
    # Check if the sign bit is set
    if value & (1 << 12):
        # If set, extend with 1s
        return (value & 0x1FFF) - 0x2000
    else:
        # Otherwise, extend with 0s
        return value & 0x1FFF

# Function to decode R-type instruction
# Robert Palermo
def decode_R(instr, opcode):
    rd = (instr >> 7) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    funct7 = (instr >> 25) & 0x7F

    #print("Instruction Type: R")
    if funct7 == 0b00000000:
        if (funct3 | (funct7 << 3)) == 0b0000000:
            #print("Operation: add")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000001:
            #print("Operation: sll")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000101:
            #print("Operation: srl")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000010:
            #print("Operation: slt")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000011:
            #print("Operation: sltu")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000100:
            #print("Operation: xor")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000110:
            #print("Operation: or")
            pass
        elif (funct3 | (funct7 << 3)) == 0b0000111:
            #print("Operation: and")
            pass
    elif funct7 == 0b0100000:
        if funct3 == 0b000:
            #print("Operation: sub")
            pass
        elif funct3 == 0b101:
            #print("Operation: sra")
            pass

    # print(f"Rs1: x{rs1}")
    # print(f"Rs2: x{rs2}")
    # print(f"Rd: x{rd}")
    # print(f"Funct3: {funct3}")
    # print(f"Funct7: {funct7}")
    # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, rs1, rs2, "NA", funct3, funct7

# Function to decode I-type instruction
# Ronald Chen
def decode_I(instr):
    rd = (instr >> 7) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12((instr >> 20) & 0x5F) # Sign extend immediate

    #print("Instruction Type: I")
    if opcode == 0b0000011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            #print("Operation: lb")
            pass
        elif funct3 == 0b010:
            print("Operation: lw")
            pass
        elif funct3 == 0b001:
            #print("Operation: lh")
            pass
    elif opcode == 0b0010011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            #print("Operation: addi")
            pass
        elif funct3 == 0b001:
            #print("Operation: slli")
            pass
        elif funct3 == 0b111:
            #print("Operation: andi")
            pass
        elif funct3 == 0b110:
            #print("Operation: ori")
            pass
        elif funct3 == 0b100:
            #print("Operation: xori")
            pass
        elif funct3 == 0b010:
            #print("Operation: slti")
            pass
        elif funct3 == 0b011:
            #print("Operation: sltiu")
            pass
        elif funct3 == 0b101:
            shtype = instr >> 25
            if shtype == 0b0000000:
                #print("Operation: srli")
                pass
            elif shtype == 0b0100000:
                #print("Operation: srai")
                pass

    # print(f"Rs1: x{rs1}")
    # print(f"Rd: x{rd}")
    # print(f"Immediate: {imm}", end="")
    # if imm < 0 or imm > 9:
    #     print(f" (or 0x{imm & 0x5F:X})", end="")
    # print()
    # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, rs1, "NA", imm, "NA", "NA"

# Function to decode S-type instruction
# Robert Palermo
def decode_S(instr):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12(((instr >> 25) << 5) | ((instr >> 7) & 0x1F)) # Sign extend immediate

    #print("Instruction Type: S")
    if opcode == 0b0100011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            #print("Operation: sb")
            pass
        elif funct3 == 0b001:
            #print("Operation: sh")
            pass
        elif funct3 == 0b010:
            print("Operation: sw")
            pass

    # print(f"Rs1: x{rs1}")
    # print(f"Rs2: x{rs2}")
    # print(f"Immediate: {imm}", end="")
    # if imm < 0 or imm > 9:
    #     print(f" (or 0x{imm & 0xFFF:X})", end="")
    # print()
    # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, "NA", rs1, rs2, imm, funct3, "NA"

# Function to decode SB-type instruction
# Ronald Chen
def decode_SB(instr, opcode):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    imm = sign_extend_13(((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) |
                         (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)) # Sign extend immediate

    #print("Instruction Type: SB")
    if funct3 == 0b000:
        #print("Operation: beq")
        pass
    elif funct3 == 0b101:
        #print("Operation: bge")
        pass
    elif funct3 == 0b100:
        #print("Operation: blt")
        pass
    elif funct3 == 0b001:
        #print("Operation: bne")
        pass

    # print(f"Rs1: x{rs1}")
    # print(f"Rs2: x{rs2}")
    # print(f"Immediate: {imm}", end="")
    # if imm < 0 or imm > 9:
    #     print(f" (or 0x{imm & 0xFFF:X})", end="")
    # print()
    # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, "NA", rs1, rs2, imm, funct3, "NA"

# Function to decode UJ-type instruction
# Robert Palermo
def decode_UJ(instr):
    rd = (instr >> 7) & 0x1F
    opcode = instr & 0x7F
    imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) | \
          (((instr >> 20) & 0x1) << 11) | (((instr >> 21) & 0x3FF) << 1)

    #print("Instruction Type: UJ")
    if opcode == 0b1101111:
        #print("Operation: jal")
        pass

    # print(f"Rd: x{rd}")
    # print(f"Immediate: {imm}", end="")
    # if imm < 0 or imm > 9:
    #     print(f" (or 0x{imm & 0xFFF:X})", end="")
    # print()
    # opcode, rd, rs1, rs2, imm, funct3, funct7
    return opcode, rd, "NA", "NA", imm, "NA", "NA"

# Robert Palermo
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