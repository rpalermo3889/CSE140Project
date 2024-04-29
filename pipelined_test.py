import decoder

class PipelineRegister:
    def __init__(self):
        self.instruction = None
        # Add member variables for individual stage's output signals
        # Decode outputs
        self.opcode = 0
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.funct3 = 0
        self.funct7 = 0

        # Control signals
        self.RegWrite = 0
        self.Branch = 0
        self.ALUSrc = 0
        self.MemWrite = 0
        self.MemtoReg = 0
        self.MemRead = 0
        self.Jump = 0

        # Additional varibales
        self.pc = 0
        self.alu_zero = 0
        self.branch_target = 0
        self.alu_ctrl = 0
        self.ALUOp = 0

# Global variables
total_clock_cycles = 0

# Pipeline stage registers
if_id = PipelineRegister()
id_ex = PipelineRegister()
ex_mem = PipelineRegister()
mem_wb = PipelineRegister()
ctrl_ex = PipelineRegister()

#=============================================== Part_1 ========================================================
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

def Fetch(lines, total_lines):
    # Read instruction from program text file based on pc value
    pc += 4
    next_pc = pc
    # Update branch_target if needed
    if alu_zero != 0:
        pc += branch_target
    else:
        pc = next_pc
    
    # Calculate which instruction line
    # PC is divided by 4, since each increment of 4 depicts a new instruction
    # Getting the modulus of it with the total number of lines allows it to wrap around the count
    # Minus 1 is to account that the first instruction is in the 0th element.
    line_number = int((pc/4) % total_lines) - 1
    current_line = lines[line_number]
    
    # Output to Decode
    if_id.pc, if_id.branch_target, if_id.alu_zero

    return pc, current_line

def Decode(instruction):
    # Input from Fetch
    instruction = if_id.pc

    # Extract opcode and operands from instruction
    opcode, rd, rs1, rs2, imm, funct3, funct7 = decoder.decoder(instruction)

    # Output to Execute
    id_ex.opcode = opcode
    id_ex.rd = rd
    id_ex.rs1 = rs1
    id_ex.rs2 = rs2
    id_ex.imm = imm
    id_ex.funct3 = funct3
    id_ex.funct7 = funct7

    return opcode, rd, rs1, rs2, imm, funct3, funct7

def Execute(alu_ctrl, rs1, rs2, imm, MemtoReg):
    # Input from Decode
    alu_ctrl = ctrl_ex.alu_ctrl
    MemtoReg = ctrl_ex.MemtoReg
    rs1 = id_ex.rs1
    rs2 = id_ex.rs2
    imm = id_ex.imm
    
    #global alu_zero, branch_target, d_mem, rf
    # Perform ALU operation
    ALUOp = 0

    if rs1 != "NA":
        rs1_value = rf[rs1]
    if rs2 != "NA":
        rs2_value = rf[rs2]

    # ALU operations
    if alu_ctrl == 0:         # jal
        pass

    elif alu_ctrl == 0b0000:  # AND
        ALUOp = rs1_value and rs2_value

    elif alu_ctrl == 0b0001:  # OR
        ALUOp = rs1_value | rs2_value

    elif alu_ctrl == 0b0010:  # add
        if MemtoReg == 1:
            ALUOp = rs1_value + imm
        else:
            ALUOp = rs1_value + rs2_value
    
    elif alu_ctrl == 0b0110:  # sub
        ALUOp = rs1_value - rs2_value

        if rs1_value == rs2_value:
            branch_target = imm  # Branch target address is the immediate value
        else:
            branch_target = 0  # For other instructions, branch target address remains 0

    # Set zero flag if result is zero
    if ALUOp == 0:
        alu_zero = 1

    # Output to Mem
    ex_mem.ALUOp = ALUOp
    ex_mem.alu_zero = alu_zero
    ex_mem.branch_target = branch_target
    
    return ALUOp, alu_zero, branch_target

def Mem(MemRead, MemWrite, rs2):
    global rf
    # Input from Execute
    ALUSrc = ex_mem.ALUSrc
    ALUOp = ex_mem.ALUOp
    MemRead = ex_mem.MemRead
    MemWrite = ex_mem.MemWrite

    mem_address = ALUOp if ALUSrc == 1 else rs2  # Memory address for lw/sw      # also jalr?
    write_data = rf[rs2] if rs2 != "NA" else rs2 # Data to write to memory for sw

    if MemRead:
        read_data = d_mem[mem_address]
    else:
        read_data = None

    if MemWrite:
        d_mem[mem_address] = write_data
    
    # Output to Writeback
    mem_wb.MemRead = MemRead
    mem_wb.MemWrite = MemWrite

    return mem_address, write_data, read_data

def Writeback(rd, rs1, imm, read_data):
    # global total_clock_cycles, pc, rf, MemRead, Jump, ALUSrc, ALUOp, RegWrite
    global rf
    
    rd = mem_wb.rd
    rs1 = mem_wb.rs1
    imm = mem_wb.imm
    # total_clock_cycles ???
    pc = mem_wb.pc
    # rf ????
    MemRead = mem_wb.MemRead
    Jump = mem_wb.Jump
    ALUSrc = mem_wb.ALUSrc
    ALUOp = mem_wb.ALUOp
    RegWrite = mem_wb.RegWrite

    # Increment total clock cycles
    total_clock_cycles += 1

    if RegWrite == 1:
        if Jump == 1 and ALUSrc == 0:       # jal
            # Update destination register with PC+4 value
            rf[rd] = pc
            # Jump to target address
            pc = (pc - 4) + imm
                
        elif Jump == 1 and ALUSrc == 1:     #jalr
            # Update destination register with PC+4 value
            curr_pc = pc
            # Jump to target address
            pc = rf[rs1] + imm
            rf[rd] = curr_pc

        else:
            # Other instructions
            if rd != "NA":
                rf[rd] = read_data if MemRead == 1 else ALUOp

    return total_clock_cycles

def ControlUnit(opcode, funct3, funct7):
    # Control signals
    #global RegWrite, Branch, ALUSrc, alu_ctrl, MemWrite, MemtoReg, MemRead, Jump

    RegWrite = 0
    MemRead = 0
    MemWrite = 0
    MemtoReg = 0
    Branch = 0
    ALUSrc = 0
    alu_ctrl = 0
    Jump = 0

    '''
    S: sw
    SB: beq
    I: addi, ori, andi, lw
    R: add, and, or, sub
    '''

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

    elif opcode == 0b0010011: # I-type
        RegWrite = 1
        ALUSrc = 1
        if funct3 == 0b000: # addi
            MemtoReg = 1
            alu_ctrl = 0b0010  # ALU: add
        elif funct3 == 0b110: # ori
            alu_ctrl = 0b0001  # ALU: OR
        elif funct3 == 0b111: # andi
            alu_ctrl = 0b0000  # ALU: AND

    elif opcode == 0b1100111: # jalr
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

    ctrl_ex.RegWrite = RegWrite
    ctrl_ex.MemRead = MemRead
    ctrl_ex.MemWrite = MemWrite
    ctrl_ex.Branch = Branch
    ctrl_ex.ALUSrc = ALUSrc
    ctrl_ex.alu_ctrl = alu_ctrl
    ctrl_ex.Jump = Jump
    ctrl_ex.MemtoReg = MemtoReg

    return RegWrite, MemRead, MemWrite, Branch, ALUSrc, alu_ctrl, Jump, MemtoReg

# Dictionary containing the names for each register
register_names = {
    0: "zero", 1: "ra", 2: "s0", 3: "gp", 4: "tp",
    5: "t0", 6: "t1", 7: "t2",
    8: "s0", 9: "s1",
    10: "a0", 11: "a1", 12: "a2", 13: "a3", 
    14: "a4", 15: "a5", 16: "a6", 17: "a7",
    18: "s2", 19: "s3", 20: "s4", 21: "s5", 
    22: "s6", 23: "s7", 24: "s8", 25: "s9", 
    26: "s10", 27: "s11", 
    28: "t3", 29: "t4", 30: "t5", 31: "t6"
}

# Main function
def main():
    global pc, branch_target, alu_zero, total_clock_cycles, rf, MemRead, Jump, ALUSrc, ALUOp, RegWrite

    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, 'r') as file:
        lines = file.readlines()
        total_lines = len(lines)

        # Fetch, Decode, Execute, Mem, and Writeback for each instruction
        for i in range(total_lines):
            # Fetch
            pc, current_line = Fetch(lines, total_lines)

            # Decode
            opcode, rd, rs1, rs2, imm, funct3, funct7 = Decode(current_line)
            
            # Control Unit
            RegWrite, MemRead, MemWrite, Branch, ALUSrc, alu_ctrl, Jump, MemtoReg = ControlUnit(opcode, funct3, funct7)

            # Execute 
            ALUOp, alu_zero, branch_target = Execute(alu_ctrl, rs1, rs2, imm, MemtoReg)

            # Mem
            mem_address = ALUOp if ALUSrc == 1 else rs2  # Memory address for lw/sw      # also jalr?
            write_data = rf[rs2] if rs2 != "NA" else rs2 # Data to write to memory for sw

            # Mem
            mem_address, write_data, read_data = Mem(MemRead, MemWrite, rs2)

            # Writeback
            total_clock_cycles = Writeback(rd, rs1, imm, read_data)

            #===========================================Output==========================================================
            # Print results for part 2
            rd_name = register_names.get(rd, f"x{rd}")  # Default to "x{rd}" if rd not found in dictionary
            
            if Branch:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"pc is modified to 0x{pc:x}")
            
            elif MemWrite:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                print(f"memory 0x{mem_address:x} is modified to 0x{write_data:x}")
                print(f"pc is modified to 0x{pc:x}")

            elif MemRead:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")
                
                print(f"x{rd} is modified to 0x{read_data:x}")         # for part_1
                #print(f"{rd_name} is modified to 0x{read_data:x}")      # for part_2
                
                print(f"pc is modified to 0x{pc:x}")

            elif RegWrite or Jump:
                print(f"\ntotal_clock_cycles {total_clock_cycles} :")

                print(f"x{rd} is modified to 0x{rf[rd]:x}")            # for part_1
                #print(f"{rd_name} is modified to 0x{rf[rd]:x}")         # for part_2

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