
import math

# Function to sign-extend a 12-bit immediate value
# Ronald Chen
def sign_extend_12(imm):
    if imm & 0x800: # Check if the sign bit is set
        imm |= 0xFFFFF000 # Perform sign extension
    return imm # Cast to signed int

# Function to sign-extend a 13-bit immediate value
# Ronald Chen
def sign_extend_13(imm):
    if imm & 0x1000: # Check if the sign bit is set
        imm |= 0xFFFFE000 # Perform sign extension
    return int(imm) # Cast to signed int

# Function to decode R-type instruction
# Robert Palermo
def decode_R(instr):
    rd = (instr >> 7) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    funct7 = (instr >> 25) & 0x7F

    print("Instruction Type: R")
    if funct7 == 0b00000000:
        if (funct3 | (funct7 << 3)) == 0b0000000:
            print("Operation: add")
        elif (funct3 | (funct7 << 3)) == 0b0000001:
            print("Operation: sll")
        elif (funct3 | (funct7 << 3)) == 0b0000101:
            print("Operation: srl")
        elif (funct3 | (funct7 << 3)) == 0b0000010:
            print("Operation: slt")
        elif (funct3 | (funct7 << 3)) == 0b0000011:
            print("Operation: sltu")
        elif (funct3 | (funct7 << 3)) == 0b0000100:
            print("Operation: xor")
        elif (funct3 | (funct7 << 3)) == 0b0000110:
            print("Operation: or")
        elif (funct3 | (funct7 << 3)) == 0b0000111:
            print("Operation: and")
    elif funct7 == 0b0100000:
        if funct3 == 0b000:
            print("Operation: sub")
        elif funct3 == 0b101:
            print("Operation: sra")

    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Rd: x{rd}")
    print(f"Funct3: {funct3}")
    print(f"Funct7: {funct7}")

# Function to decode I-type instruction
# Ronald Chen
def decode_I(instr):
    rd = (instr >> 7) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12((instr >> 20) & 0x5F) # Sign extend immediate

    print("Instruction Type: I")
    if opcode == 0b0000011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            print("Operation: lb")
        elif funct3 == 0b010:
            print("Operation: lw")
        elif funct3 == 0b001:
            print("Operation: lh")
    elif opcode == 0b0010011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            print("Operation: addi")
        elif funct3 == 0b001:
            print("Operation: slli")
        elif funct3 == 0b111:
            print("Operation: andi")
        elif funct3 == 0b110:
            print("Operation: ori")
        elif funct3 == 0b100:
            print("Operation: xori")
        elif funct3 == 0b010:
            print("Operation: slti")
        elif funct3 == 0b011:
            print("Operation: sltiu")
        elif funct3 == 0b101:
            shtype = instr >> 25
            if shtype == 0b0000000:
                print("Operation: srli")
            elif shtype == 0b0100000:
                print("Operation: srai")

    print(f"Rs1: x{rs1}")
    print(f"Rd: x{rd}")
    print(f"Immediate: {imm}", end="")
    if imm < 0 or imm > 9:
        print(f" (or 0x{imm & 0x5F:X})", end="")
    print()

# Function to decode S-type instruction
# Robert Palermo
# Function to decode S-type instruction
# Robert Palermo
# Function to decode S-type instruction
# Robert Palermo
def decode_S(instr):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    opcode = instr & 0x7F
    imm = sign_extend_12(((instr >> 25) << 5) | ((instr >> 7) & 0x1F)) # Sign extend immediate

    print("Instruction Type: S")
    if opcode == 0b0100011:
        funct3 = (instr >> 12) & 0b111
        if funct3 == 0b000:
            print("Operation: sb")
        elif funct3 == 0b001:
            print("Operation: sh")
        elif funct3 == 0b010:
            print("Operation: sw")

    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Immediate: {imm}", end="")
    if imm < 0 or imm > 9:
        print(f" (or 0x{imm & 0xFFF:X})", end="")
    print()


# Function to decode SB-type instruction
# Ronald Chen
def decode_SB(instr):
    rs2 = (instr >> 20) & 0x1F
    rs1 = (instr >> 15) & 0x1F
    funct3 = (instr >> 12) & 0x7
    imm = sign_extend_13(((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) |
                         (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)) # Sign extend immediate

    print("Instruction Type: SB")
    if funct3 == 0b000:
        print("Operation: beq")
    elif funct3 == 0b101:
        print("Operation: bge")
    elif funct3 == 0b100:
        print("Operation: blt")
    elif funct3 == 0b001:
        print("Operation: bne")

    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Immediate: {imm}", end="")
    if imm < 0 or imm > 9:
        print(f" (or 0x{imm & 0xFFF:X})", end="")
    print()

# Function to decode UJ-type instruction
# Robert Palermo
def decode_UJ(instr):
    rd = (instr >> 7) & 0x1F
    opcode = instr & 0x7F
    imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) | \
          (((instr >> 20) & 0x1) << 11) | (((instr >> 21) & 0x3FF) << 1)

    print("Instruction Type: UJ")
    if opcode == 0b1101111:
        print("Operation: jal")

    print(f"Rd: x{rd}")
    print(f"Immediate: {imm}", end="")
    if imm < 0 or imm > 9:
        print(f" (or 0x{imm & 0xFFF:X})", end="")
    print()

# Robert Palermo
def main():
    binary = input("Enter an instruction: ")
    instr = 0
    for i, bit in enumerate(binary):
        if bit == '1':
            instr |= (1 << (31 - i))

    opcode = instr & 0x7F
    if opcode == 0b0110011: # R-type
        decode_R(instr)
    elif opcode == 0b0000011 or opcode == 0b0010011 or opcode == 0b1100111: # I-type
        decode_I(instr)
    elif opcode == 0b0100011: # S-type
        decode_S(instr)
    elif opcode == 0b1100011: # SB-type
        decode_SB(instr)
    elif opcode == 0b1101111: # UJ-type
        decode_UJ(instr)

if __name__ == "__main__":
    main()

