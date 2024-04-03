# Global variables
pc = 0
next_pc = 0
branch_target = 0
alu_zero = 0
total_clock_cycles = 0

# Initialize register file (rf)
rf = [0] * 32
rf[1] = 0x20
rf[2] = 0x5
rf[10] = 0x70
rf[11] = 0x4

# Initialize data memory (d_mem)
d_mem = [0] * 32
d_mem[7] = 0x5
d_mem[9] = 0x10

def Fetch():
    global pc, next_pc, branch_target
    # Read instruction from input program text file
    # Increment pc by 4
    pc = next_pc
    next_pc += 4
    # Choose next_pc or branch_target based on condition (to be implemented later)


def Decode(instr):
    opcode = instr >> 25

    # Extract fields based on instruction type
    if opcode == 0b0110011:  # R-type
        # Extract register IDs and funct7, funct3 fields
        rd = (instr >> 7) & 0x1F
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct3 = (instr >> 12) & 0x7
        funct7 = (instr >> 25) & 0x7F
        # Return decoded instruction
        return ("R", rd, rs1, rs2, funct3, funct7)

    elif opcode == 0b0000011 or opcode == 0b0010011 or opcode == 0b1100111:  # I-type
        # Extract register IDs and immediate value
        rd = (instr >> 7) & 0x1F
        rs1 = (instr >> 15) & 0x1F
        imm = (instr >> 20) & 0xFFF  # 12-bit immediate
        # Perform sign extension for I-type instructions
        if imm & 0x800:  # Check if sign bit is set
            imm |= 0xFFFFF000  # Perform sign extension
        # Return decoded instruction
        return ("I", rd, rs1, imm)

    elif opcode == 0b0100011:  # S-type
        # Extract register IDs and immediate value
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        imm = ((instr >> 25) << 5) | ((instr >> 7) & 0x1F)  # 12-bit immediate
        # Perform sign extension for S-type instructions
        if imm & 0x800:  # Check if sign bit is set
            imm |= 0xFFFFF000  # Perform sign extension
        # Return decoded instruction
        return ("S", rs1, rs2, imm)
    
    elif opcode == 0b1100011:  # SB-type
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct3 = (instr >> 12) & 0x7
        imm = ((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) | (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)
        # Perform sign extension for S-type instructions
        if imm & 0x1000:  # Check if sign bit is set
            imm |= 0xFFFFE000  # Perform sign extension
        # Return decoded instruction
        return ("SB", rs1, rs2, imm)

    elif opcode == 0b1101111:  # UJ-type
        # Extract register ID and immediate value
        rd = (instr >> 7) & 0x1F
        imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) | (((instr >> 20) & 0x1) << 11) | (((instr >> 21) & 0x3FF) << 1)  # 20-bit immediate
        # Return decoded instruction
        return ("UJ", rd, imm)

    else:
        raise ValueError("Unsupported opcode")

def Execute(alu_ctrl, rs1_val, rs2_val, imm):
    global alu_zero, branch_target

    # Perform ALU operations based on alu_ctrl
    if alu_ctrl == 0b0000:  # AND
        result = rs1_val & rs2_val
    elif alu_ctrl == 0b0001:  # OR
        result = rs1_val | rs2_val
    elif alu_ctrl == 0b0010:  # ADD
        result = rs1_val + rs2_val
    elif alu_ctrl == 0b0110:  # SUB
        result = rs1_val - rs2_val
    else:
        raise ValueError("Unsupported ALU operation")

    # Update alu_zero based on result
    alu_zero = int(result == 0)

    # Calculate branch target address
    branch_target = (imm << 1) + pc
    # Add PC+4 to branch_target to get the absolute address
    branch_target += 4

def Mem(address, data=None, is_store=False):
    if is_store:
        # Store data to memory at the specified address for SW instruction
        d_mem[address >> 2] = data
    else:
        # Load data from memory at the specified address for LW instruction
        return d_mem[address >> 2]

def Writeback(rd, result=None, mem_data=None):
    global total_clock_cycles

    if result is not None:
        # Update destination register with computation result from ALU
        rf[rd] = result
    elif mem_data is not None:
        # Update destination register with data from data memory
        rf[rd] = mem_data

    # Increment total clock cycles
    total_clock_cycles += 1

def ControlUnit(opcode):
    global RegWrite, Branch, MemRead, MemWrite, MemtoReg, ALUOp, ALUSrc

    # Reset control signals
    RegWrite = 0
    Branch = 0
    MemRead = 0
    MemWrite = 0
    MemtoReg = 0
    ALUOp = 0
    ALUSrc = 0

    # Set control signals based on opcode
    if opcode == 0b0000011:  # LW
        RegWrite = 1
        MemRead = 1
        MemtoReg = 1
        ALUSrc = 1
    elif opcode == 0b0100011:  # SW
        MemWrite = 1
        ALUSrc = 1
    elif opcode == 0b0010011:  # ALU immediate
        RegWrite = 1
        ALUSrc = 1
    elif opcode == 0b0110011:  # ALU register
        RegWrite = 1
        ALUOp = 1
    elif opcode == 0b1100011:  # Branch
        Branch = 1
    elif opcode == 0b1101111:  # Jump and link
        RegWrite = 1
    else:
        raise ValueError("Unsupported opcode")

    # Return control signals
    return RegWrite, Branch, MemRead, MemWrite, MemtoReg, ALUOp, ALUSrc

def main():
    global pc, next_pc, total_clock_cycles

    # Initialize PC and clock cycles
    pc = 0
    next_pc = 0
    total_clock_cycles = 0

    # Initialize registers and memory
    rf[1] = 0x20
    rf[2] = 0x5
    rf[10] = 0x70
    rf[11] = 0x4
    d_mem[0x70 >> 2] = 0x5
    d_mem[0x74 >> 2] = 0x10

    # Load program instructions from file
    with open("sample_part1.txt", "r") as file:
        instructions = file.readlines()

    # Execute program instructions
    while pc < len(instructions):
        instr = int(instructions[pc].strip(), 2)  # Convert binary string to integer
        Fetch()  # Fetch instruction
        decoded_instr = Decode(instr)  # Decode instruction
        ControlUnit(decoded_instr[0])  # Generate control signals
        Execute(*decoded_instr[1:])  # Execute instruction
        Mem()  # Access memory
        Writeback()  # Write back results to register file

        # Print modified contents of rf and d-mem arrays
        print("Modified contents of register file (rf):", rf)
        print("Modified contents of data memory (d_mem):", d_mem)
        print("Total clock cycles:", total_clock_cycles)
        print("PC:", pc)

        # Update PC based on branch instructions
        pc = branch_target if Branch else next_pc

# Run the main function
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