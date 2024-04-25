import decoder
# Global variables
pc = 0
branch_target = 0
alu_zero = 0
total_clock_cycles = 0

# Control signals
RegWrite = 0
Branch = 0
ALUSrc = 0
ALUOp = 0
MemWrite = 0
MemtoReg = 0
MemRead = 0
Jump = 0
Link = 0

# Register file initialization
#========================================================
# Part_1
# x1 = 0x20, x2 = 0x5, x10 = 0x70, x11 = 0x4

# rf = [0] * 32
# rf[1] = 0x20
# rf[2] = 0x5
# rf[10] = 0x70
# rf[11] = 0x4

# Part_2
# s0 = 0x20, a0 = 0x5, a1 = 0x2, a2 = 0xa, a3 = 0xf

rf = [0] * 32
rf[8] = 0x20  # s0
rf[10] = 0x5  # a0
rf[11] = 0x2  # a1
rf[12] = 0xa  # a2
rf[13] = 0xf  # a3

#========================================================

# Data memory initialization
# 0x70 = 0x5, 0x74 = 0x10
d_mem = [0] * (0x74 + 1)  # Increase size of the data memory to 64 entries
d_mem[0x70] = 0x5
d_mem[0x74] = 0x10

def Fetch():
    global pc, branch_target
    # Read instruction from program text file based on pc value
    # Increment pc by 4
    pc += 4
    next_pc = pc
    # Update branch_target if needed
    if branch_target != 0:
        pc += branch_target
    else:
        pc = next_pc
    return pc

# TODO: add a logic for pc to "jump" (jal & jalr)

def Decode(instruction):
    # Extract opcode and operands from instruction
    opcode, rd, rs1, rs2, imm, funct3, funct7 = decoder.decoder(instruction)

    return opcode, rd, rs1, rs2, imm, funct3, funct7

def Execute(ALUOp, rs1, rs2, imm):
    global alu_zero, branch_target, d_mem, rf
    # Perform ALU operation
    alu_ctrl = 0

    if rs1 != "NA":
        rs1_value = rf[rs1]
    if rs2 != "NA":
        rs2_value = rf[rs2]
    
    # ALU operations
    if ALUOp == 0:         # jal & jalr
        pass

    elif ALUOp == 0b0000:  # AND
        alu_ctrl = rs1_value and rs2_value

    elif ALUOp == 0b0001:  # OR
        alu_ctrl = rs1_value | rs2_value

    elif ALUOp == 0b0010:  # add
        if imm != "NA":
            alu_ctrl = rs1_value + imm
        else:
            alu_ctrl = rs1_value + rs2_value
    
    elif ALUOp == 0b0110:  # sub
        alu_ctrl = rs1_value - rs2_value

        if rs1_value == rs2_value:
            branch_target = imm  # Branch target address is the immediate value
        else:
            branch_target = 0  # For other instructions, branch target address remains 0
        
    # Set zero flag if result is zero
    if alu_ctrl == 0:
        alu_zero = 1
    
    return alu_ctrl, alu_zero, branch_target

def Mem(mem_address, write_data, MemRead, MemWrite):
    # mem_address %= 64  # Ensure memory address wraps around if it exceeds array size

    if MemRead:
        read_data = d_mem[mem_address]
    else:
        read_data = None

    if MemWrite:
        d_mem[mem_address] = write_data

    return read_data

def Writeback():
    global total_clock_cycles
    
    # Increment total clock cycles
    total_clock_cycles += 1

    return total_clock_cycles

def ControlUnit(opcode, funct3, funct7):
    # Control signals
    global RegWrite, Branch, ALUSrc, ALUOp, MemWrite, MemtoReg, MemRead, Jump, Link
    RegWrite = 0
    MemRead = 0
    MemWrite = 0
    Branch = 0
    ALUSrc = 0
    ALUOp = 0
    Jump = 0
    Link = 0

    '''
    S: sw
    SB: beq
    I: addi, ori, andi, lw
    R: add, and, or, sub
    '''

    if opcode == 0b0100011:  # sw
        MemWrite = 1
        ALUSrc = 1
        ALUOp = 0b0010  # add 
    
    elif opcode == 0b1100011:  # beq
        Branch = 1
        ALUOp = 0b0110  # ALU: sub
    
    elif opcode == 0b0000011:  # lw
        MemRead = 1
        ALUSrc = 1
        RegWrite = 1
        MemtoReg = 1
        ALUOp = 0b0010  # ALU: add

    elif opcode == 0b0010011: # I-type
        RegWrite = 1
        ALUSrc = 1
        if funct3 == 0b000: # addi
            ALUOp = 0b0010  # ALU: add
        elif funct3 == 0b110: # ori
            ALUOp = 0b0001  # ALU: OR
        elif funct3 == 0b111: # andi
            ALUOp = 0b0000  # ALU: AND
    
    elif opcode == 0b1100111: # jalr
        RegWrite = 1
        ALUSrc = 1
        Jump = 1
        Link = 1
    
    elif opcode == 0b0110011:  # R-type
        RegWrite = 1
        if funct7 == 0b0000000:
            if funct3 == 0b000:  # add
                ALUOp = 0b0010  # ALU: add
            elif funct3 == 0b110:  # or
                ALUOp = 0b0001  # ALU: OR
            elif funct3 == 0b111:  # and
                ALUOp = 0b0000  # ALU: AND
        elif funct7 == 0b0100000:
            if funct3 == 0b000:  # sub
                ALUOp = 0b0110  # ALU: sub
    
    elif opcode == 0b1101111:  # jal
        Jump = 1
        Link = 1

    return RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp, Jump, Link

# Main function
def main():
    global pc, branch_target, alu_zero

    # Ask the user for the filename
    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, "r") as file:
        # Fetch, Decode, Execute, Mem, and Writeback for each instruction
        for line in file:
            # Fetch
            pc = Fetch()
            opcode, rd, rs1, rs2, imm, funct3, funct7 = Decode(line)
            
            # Control Unit
            RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp, Jump, Link = ControlUnit(opcode, funct3, funct7)

            # Execute 
            alu_ctrl, alu_zero, branch_target = Execute(ALUOp, rs1, rs2, imm)

            # Mem
            mem_address = alu_ctrl if ALUSrc == 1 else rs2  # Memory address for lw/sw
            write_data = rf[rs2] if rs2 != "NA" else rs2 # Data to write to memory for sw
            read_data = Mem(mem_address, write_data, MemRead, MemWrite)

            # Writeback
            total_clock_cycles = Writeback()
            if RegWrite == 1:
                if Jump == 1:
                    if Link == 1:
                        # Update destination register with PC+4 value
                        rf[rd] = pc
                    # Jump to target address
                    pc = pc + imm
                else:
                    # Other instructions
                    if rd != "NA":
                        rf[rd] = read_data if MemRead == 1 else alu_ctrl

            # Print results
            # TODO: fix output to use correct register and changes
            if Jump:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"{rd} is modified to 0x{rf[rd]:x}")
                print(f"pc is modified to 0x{pc:x}")

            elif Branch:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"pc is modified to 0x{pc:x}")
            
            elif MemWrite:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"memory 0x{mem_address:x} is modified to 0x{write_data:x}")
                print(f"pc is modified to 0x{pc:x}")

            elif MemRead:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"x{rd} is modified to 0x{read_data:x}")
                print(f"pc is modified to 0x{pc:x}")

            elif RegWrite:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"x{rd} is modified to 0x{rf[rd]:x}")
                print(f"pc is modified to 0x{pc:x}")
            
            else:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :\nNo memory operation performed.")

    print("\nprogram terminated:")
    print(f"total execution time is {total_clock_cycles} cycles")

if __name__ == "__main__":
    main()

# sample_part2.txt
"""
00000000100000000000000011101111
00000001000000000000000011101111
00000000110001011000010100110011
01000000101001101000111100110011
00000000000000001000000011100111
00000001111001000010000000100011

Translations:
jal x1, 8           {rd: x1}                        (output: ra is modified to 0x4)          
jal x1, 16          {rd: x1}                        (output: a0 is modified to 0xc)      

add x10, x11, x12   {rd: x10, rs1: x11, rs2: x12}   (output: t5 is modified to 0x3)
sub x30, x13, x10   {rd: x30, rs1: x13, rs2: x10}   (output: ra is modified to 0x14)

jalr x1, 0(x1)      {rd: x1, rs1: x1}               (output: ra is modified to 0x8)

sw x30, 0(x8)       {rs1: x8, rs2: x30}             (output: memory 0x20 is modified to 0x3)

Current Output:
Enter the program file name to run:
sample_part2.txt

 Operation: jal
total_clock_cycles 1 :
1 is modified to 0x0                    # ra is modified to 0x4
pc is modified to 0x4                   # pc is modified to 0x8

 Operation: jal
total_clock_cycles 2 :
1 is modified to 0x0                    # a0 is modified to 0xc
pc is modified to 0x8                   # pc is modified to 0xc

 Operation: add
total_clock_cycles 3 :
x10 is modified to 0xc                  # t5 is modified to 0x3
pc is modified to 0xc                   # pc is modified to 0x10

 Operation: sub
total_clock_cycles 4 :
x30 is modified to 0x3                  # ra is modified to 0x14
pc is modified to 0x10                  # pc is modified to 0x4

 Operation: jalr
total_clock_cycles 5 :
x1 is modified to 0x14                  # ra is modified to 0x8
pc is modified to 0x14                  # pc is modified to 0x14

 Operation: sw
total_clock_cycles 6 :
memory 0x20 is modified to 0x3
pc is modified to 0x18

program terminated:
total execution time is 6 cycles


#==============================================================
Correct Output:

Enter the program file name to run:
sample_part2.txt

total_clock_cycles 1 :
ra is modified to 0x4
pc is modified to 0x8

total_clock_cycles 2 :
a0 is modified to 0xc
pc is modified to 0xc

total_clock_cycles 3 :
t5 is modified to 0x3
pc is modified to 0x10

total_clock_cycles 4 :
ra is modified to 0x14
pc is modified to 0x4

total_clock_cycles 5 :
ra is modified to 0x8
pc is modified to 0x14

total_clock_cycles 6 :
memory 0x20 is modified to 0x3
pc is modified to 0x18

program terminated:
total execution time is 6 cycles
#==============================================================
"""





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


Current Output:
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
"""