# Global variables
pc = 0
next_pc = 0
branch_target = 0
alu_zero = 0
total_clock_cycles = 0

# Register file initialization
rf = [0] * 32
rf[1] = 0x20
rf[2] = 0x5
rf[10] = 0x70
rf[11] = 0x4

# Data memory initialization
d_mem = [0] * 64  # Increase size of the data memory to 64 entries
d_mem[0x1C] = 0x5
d_mem[0x20] = 0x10

def Fetch():
    global pc, next_pc, branch_target
    # Read instruction from program text file based on pc value
    # Increment pc by 4
    pc += 4
    next_pc = pc
    # Update branch_target if needed
    pc = branch_target if branch_target != 0 else next_pc

def Decode(instruction):
    # Extract opcode and operands from instruction
    opcode = instruction & 0x7F
    rs1 = (instruction >> 15) & 0x1F
    rs2 = (instruction >> 20) & 0x1F
    rd = (instruction >> 7) & 0x1F
    imm = instruction >> 20  # Extract immediate field
    
    # Perform sign-extension for I-type instructions
    if imm & 0x800:
        imm |= 0xFFFFF000
    
    # Call ControlUnit to generate control signals
    RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp = ControlUnit(opcode, (instruction >> 12) & 0b111, (instruction >> 25) & 0b1111111)

    return opcode, rs1, rs2, rd, imm, RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp

def Execute(ALUOp, rs1_value, rs2_value, imm):
    # Perform ALU operation
    alu_result = 0
    zero = 0
    
    # ALU operations
    if ALUOp == 0b000:  # add
        alu_result = rs1_value + rs2_value
    elif ALUOp == 0b1001:  # sub
        alu_result = rs1_value - rs2_value
    # Other ALU operations can be added here
    
    # Calculate branch target address
    branch_target = 0
    if ALUOp == 0b001:  # beq
        branch_target = imm  # Branch target address is the immediate value
    else:
        branch_target = 0  # For other instructions, branch target address remains 0
    
    # Set zero flag if result is zero
    if alu_result == 0:
        zero = 1
    
    return alu_result, zero, branch_target

def Mem(mem_address, write_data, MemRead, MemWrite):
    mem_address %= 64  # Ensure memory address wraps around if it exceeds array size

    if MemRead:
        read_data = d_mem[mem_address]
    else:
        read_data = None

    if MemWrite:
        d_mem[mem_address] = write_data

    return read_data

def Writeback(rd, result, RegWrite):
    if RegWrite:
        rf[rd] = result

def ControlUnit(opcode, funct3, funct7):
    # Generate control signals based on opcode and function field values
    RegWrite = 1
    MemRead = 0
    MemWrite = 0
    Branch = 0
    ALUSrc = 0
    ALUOp = 0b00  # default for add, and, or, sub

    if opcode == 0b0000011:  # lw
        MemRead = 1
        ALUSrc = 1
        ALUOp = 0b000
    elif opcode == 0b0100011:  # sw
        MemWrite = 1
        ALUSrc = 1
        ALUOp = 0b000
    elif opcode == 0b1100011:  # beq
        Branch = 1
        ALUOp = 0b001
    elif opcode == 0b0110011:  # R-type
        if funct7 == 0b0000000:
            if funct3 == 0b000:  # add
                ALUOp = 0b000
            elif funct3 == 0b001:  # sll
                ALUOp = 0b010
            elif funct3 == 0b010:  # slt
                ALUOp = 0b011
            elif funct3 == 0b011:  # sltu
                ALUOp = 0b100
            elif funct3 == 0b100:  # xor
                ALUOp = 0b101
            elif funct3 == 0b101:  # srl
                ALUOp = 0b110
            elif funct3 == 0b110:  # or
                ALUOp = 0b111
            elif funct3 == 0b111:  # and
                ALUOp = 0b1000
        elif funct7 == 0b0100000:
            if funct3 == 0b000:  # sub
                ALUOp = 0b1001
            elif funct3 == 0b101:  # sra
                ALUOp = 0b1101

    return RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp

# Main function
def main():
    # Initialize registers and memory
    rf = [0] * 32  # Register file with 32 entries
    rf[1] = 0x20
    rf[2] = 0x5
    rf[10] = 0x70
    rf[11] = 0x4

    d_mem = [0] * 64  # Increase size of the data memory to 64 entries
    d_mem[0x1C] = 0x5
    d_mem[0x20] = 0x10

    pc = 0  # Program counter
    total_clock_cycles = 0  # Total clock cycles

    # Ask the user for the filename
    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, "r") as file:
        instructions = [int(line.strip(), 2) for line in file]

    # Fetch, Decode, Execute, Mem, and Writeback for each instruction
    for instr in instructions:
        # Fetch
        opcode, rs1, rs2, rd, imm, RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp = Decode(instr)
        
        # Control Unit
        RegWrite, MemRead, MemWrite, Branch, ALUSrc, ALUOp = ControlUnit(opcode, (instr >> 12) & 0b111, (instr >> 25) & 0b1111111)

        # Execute
        rs1_value = rf[rs1]
        rs2_value = rf[rs2]
        alu_result, zero, branch_target = Execute(ALUOp, rs1_value, rs2_value, imm)
        
        # Mem
        mem_address = alu_result if ALUSrc else rs2  # Memory address for lw/sw
        write_data = rs2_value if ALUSrc else rf[rd]  # Data to write to memory for sw
        read_data = Mem(mem_address, write_data, MemRead, MemWrite)
        
        # Writeback
        if RegWrite:
            rf[rd] = read_data if MemRead else alu_result
        
        # Increment total clock cycles
        total_clock_cycles += 1

        # Print results
        if MemWrite:
            print(f"\ntotal_clock_cycles {total_clock_cycles} :\nmemory 0x{mem_address:02X} is modified to 0x{write_data:02X}")
        elif Branch:
            print(f"\ntotal_clock_cycles {total_clock_cycles} :\npc is modified to 0x{branch_target:02X}")
        elif MemRead:
            print(f"\ntotal_clock_cycles {total_clock_cycles} :\nx{rd} is modified to 0x{read_data:02X}")
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
"""