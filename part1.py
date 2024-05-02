import decoder

# Global variables
pc = 0
branch_target = 0
alu_zero = 0
total_clock_cycles = 0
alu_ctrl = 0
ALUOp = 0

# Instruction lines variables
lines = []
instruction = 0

# Memory fields
mem_address = 0
write_data = 0
read_data = 0

# Decode fields
opcode = 0
rd = 0
rs1 = 0
rs2 = 0
imm = 0
funct3 = 0
funct7 = 0

# Control signals
RegWrite = 0
Branch = 0
ALUSrc = 0
MemWrite = 0
MemtoReg = 0
MemRead = 0
Jump = 0

# =============================================== Part_1 ========================================================

# Register file initialization (x1 = 0x20, x2 = 0x5, x10 = 0x70, x11 = 0x4)
rf = [0] * 32
rf[1] = 0x20
rf[2] = 0x5
rf[10] = 0x70
rf[11] = 0x4

# Data memory initialization (0x70 = 0x5, 0x74 = 0x10)
d_mem = [0] * (0x74 + 1)  # Increase size of the data memory to 64 entries
d_mem[0x70] = 0x5
d_mem[0x74] = 0x10

def Fetch():
    global pc, lines, instruction
    # Read instruction from program text file based on pc value
    next_pc = pc + 4
    pc = next_pc

    # Calculate which instruction line
    line_number = int(pc / 4) - 1
    instruction = lines[line_number]


def Decode():
    global instruction, opcode, rd, rs1, rs2, imm, funct3, funct7
    # Extract opcode and operands from instruction
    opcode, rd, rs1, rs2, imm, funct3, funct7 = decoder.decoder(instruction)


def Execute():
    global alu_ctrl, alu_zero, branch_target, rf, pc
    global ALUOp, MemtoReg
    global rs1, rs2, imm

    # Perform ALU operation
    ALUOp = 0
    alu_zero = 0

    if rs1 != "NA":
        rs1_value = rf[rs1]
    if rs2 != "NA":
        rs2_value = rf[rs2]

    # ALU operations
    if alu_ctrl == "NA":  # jal
        pass

    elif alu_ctrl == 0b0000:  # AND
        if MemtoReg == 1:
            ALUOp = rs1_value & imm
        else:
            ALUOp = rs1_value & rs2_value

    elif alu_ctrl == 0b0001:  # OR
        if MemtoReg == 1:
            ALUOp = rs1_value | imm
        else:
            ALUOp = rs1_value | rs2_value

    elif alu_ctrl == 0b0010:  # add
        if MemtoReg == 1:
            ALUOp = rs1_value + imm
        else:
            ALUOp = rs1_value + rs2_value

    elif alu_ctrl == 0b0110:  # sub
        if MemtoReg == 1:
            ALUOp = rs1_value - imm
        else:
            ALUOp = rs1_value - rs2_value

        if ALUOp == 0:
            branch_target = imm  # Branch target address is the immediate value
            alu_zero = 1  # Set zero flag
        else:
            branch_target = 0  # For other instructions, branch target address remains 0

    if alu_zero == 1:
        # Branch to target address
        pc = (pc - 4) + branch_target


def Mem():
    # Control Signals
    global ALUSrc, ALUOp, MemRead, MemWrite
    global mem_address, write_data, read_data, d_mem, rf, rs2

    mem_address = ALUOp if ALUSrc == 1 else rs2  # Memory address for lw/sw
    write_data = rf[rs2] if rs2 != "NA" else rs2  # Data to write to memory for sw

    if MemRead:
        read_data = d_mem[mem_address]
    else:
        read_data = None

    if MemWrite:
        d_mem[mem_address] = write_data


def Writeback():
    # Control Signals
    global MemRead, Jump, ALUSrc, ALUOp, RegWrite, Branch
    # Decode fields
    global rd, rs1, imm
    global total_clock_cycles, branch_target, pc, rf, read_data

    # Increment total clock cycles
    total_clock_cycles += 1

    jump_target = imm

    if RegWrite == 1:
        if Jump == 1 and ALUSrc == 0:  # jal
            # Update destination register with PC+4 value
            rf[rd] = pc
            # Jump to target address
            pc = (pc - 4) + jump_target

        elif Jump == 1 and ALUSrc == 1:  # jalr
            # Update destination register with PC+4 value
            curr_pc = pc
            # Jump to target address
            pc = rf[rs1] + jump_target
            rf[rd] = curr_pc

        else:
            # Other instructions
            if rd != "NA":
                rf[rd] = read_data if MemRead == 1 else ALUOp


def ControlUnit():
    # Control signals
    global RegWrite, Branch, MemWrite, MemtoReg, MemRead, Jump, ALUSrc
    global alu_ctrl, opcode, funct3, funct7

    RegWrite = 0
    MemRead = 0
    MemWrite = 0
    MemtoReg = 0
    Branch = 0
    ALUSrc = 0
    alu_ctrl = 0
    Jump = 0

    if opcode == 0b0100011:  # sw
        MemWrite = 1
        ALUSrc = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # add

    elif opcode == 0b1100011:  # beq
        Branch = 1
        alu_ctrl = 0b0110  # ALU: sub

    elif opcode == 0b0000011:  # lw
        MemRead = 1
        ALUSrc = 1
        RegWrite = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # ALU: add

    elif opcode == 0b0010011:  # I-type
        RegWrite = 1
        ALUSrc = 1
        MemtoReg = 1
        if funct3 == 0b000:  # addi
            alu_ctrl = 0b0010  # ALU: add
        elif funct3 == 0b110:  # ori
            alu_ctrl = 0b0001  # ALU: OR
        elif funct3 == 0b111:  # andi
            alu_ctrl = 0b0000  # ALU: AND

    elif opcode == 0b1100111:  # jalr
        RegWrite = 1
        ALUSrc = 1
        Jump = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # ALU: add

    elif opcode == 0b0110011:  # R-type
        RegWrite = 1
        if funct7 == 0b0000000:
            if funct3 == 0b000:  # add
                alu_ctrl = 0b0010  # ALU: add
            elif funct3 == 0b110:  # or
                alu_ctrl = 0b0001  # ALU: OR
            elif funct3 == 0b111:  # and
                alu_ctrl = 0b0000  # ALU: AND
        elif funct7 == 0b0100000:
            if funct3 == 0b000:  # sub
                alu_ctrl = 0b0110  # ALU: sub

    elif opcode == 0b1101111:  # jal
        RegWrite = 1
        Jump = 1
        alu_ctrl = "NA"

# Main function
def main():
    global Branch, MemWrite, MemRead, RegWrite, Jump  # Control Signals
    global mem_address, write_data, read_data  # Mem fields
    global opcode, rd, rs1, rs2, imm, funct3, funct7  # Decode fields
    global pc, rf, total_clock_cycles, lines  # Others

    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, 'r') as file:
        lines = file.readlines()

        # Fetch, Decode, Execute, Mem, and Writeback for each instruction
        while pc < len(lines) * 4:
            Fetch()
            Decode()
            ControlUnit()
            Execute()
            Mem()
            Writeback()

            # ===========================================Outputs==========================================================

            if Branch == 1:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"pc is modified to 0x{pc:x}")

            elif MemWrite == 1:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"memory 0x{mem_address:x} is modified to 0x{write_data:x}")
                print(f"pc is modified to 0x{pc:x}")

            elif MemRead == 1:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"x{rd} is modified to 0x{read_data:x}")  # for part_1
                print(f"pc is modified to 0x{pc:x}")

            elif RegWrite == 1 | Jump == 1:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"x{rd} is modified to 0x{rf[rd]:x}")  # for part_1
                print(f"pc is modified to 0x{pc:x}")

            else:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :\nNo memory operation performed.")

    print("\nprogram terminated:")
    print(f"total execution time is {total_clock_cycles} cycles")


if __name__ == "__main__":
    main()

# sample_part1.txt
"""
00000000010001010010000110000011
01000000001000001000001010110011
00000000001100101000011001100011
00000000001100101000001010110011
00000000010101011110001010110011
00000000010101010010000000100011

Translations:
lw x3, 4(x10)       {rd: x3, rs1: x10}          (output: x3 is modified to 0x10 {16})
sub x5, x1, x2      {rd: x5, rs1: 1, rs2: 2}    (output: x5 is modified to 0x1b {27})
beq x5, x3, 12      {rs1: x5, rs2: 3}

add x5, x5, x3      {rd: x5, rs1: 5, rs2: 3}    (output: x5 is modified to 0x2b {43})

or x5, x11, x5      {rd: x5, rs1: 11, rs2: x5}  (output: x5 is modified to 0x2f {47})

sw x5, 0(x10)       {rs1: x10, rs2: x5}         (output: memory 0x70 is modified to 0x2f {memory 112 is modified to 47})

sw - yes
lw - yes
jalr - yes
addi - yes
add - no

#====================== Correct Output =============================
Enter the program file name to run:
sample_part1.txt

total_clock_cycles 1 :
x3 is modified to 0x10
pc is modified to 0x4 

total_clock_cycles 2 :
x5 is modified to 0x1b
pc is modified to 0x8 

total_clock_cycles 3 :
pc is modified to 0xc 

total_clock_cycles 4 :
x5 is modified to 0x2b
pc is modified to 0x10

total_clock_cycles 5 :
x5 is modified to 0x2f
pc is modified to 0x14

total_clock_cycles 6 :
memory 0x70 is modified to 0x2f
pc is modified to 0x18

program terminated:
total execution time is 6 cycles
#==============================================================
"""