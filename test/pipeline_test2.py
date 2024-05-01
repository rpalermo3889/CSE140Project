import decoder

class PipelineRegister:
    def __init__(self):
        self.instruction = 0
        self.opcode = 0
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.funct3 = 0
        self.funct7 = 0
        self.ALU_result = 0
        self.control_signals = {
            'RegWrite': 0,
            'Branch': 0,
            'ALUSrc': 0,
            'MemWrite': 0,
            'MemtoReg': 0,
            'MemRead': 0,
            'Jump': 0
        }
        self.pc = 0
        self.read_data = 0  # New field to hold data read from memory

if_id = PipelineRegister()
id_ex = PipelineRegister()
ex_mem = PipelineRegister()
mem_wb = PipelineRegister()

# Global variables
#pc = 0
total_clock_cycles = 0
lines = []

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
    global if_id, lines, total_clock_cycles
    pc = if_id.pc

    total_clock_cycles += 1
    next_pc = pc + 4
    pc = next_pc
    
    if pc > len(lines) * 4:
        return

    if_id.pc = pc
    line_number = int(pc/4) - 1 
    if_id.instruction = lines[line_number]

def Decode():
    global if_id, id_ex
    instruction = if_id.instruction
    id_ex.opcode, id_ex.rd, id_ex.rs1, id_ex.rs2, id_ex.imm, id_ex.funct3, id_ex.funct7 = decoder.decoder(instruction)
    id_ex.control_signals = ControlUnit(id_ex.opcode, id_ex.funct3, id_ex.funct7)

    id_ex.pc = if_id.pc

    Fetch()

def Execute():
    global id_ex, ex_mem, rf
    ex_mem.opcode = id_ex.opcode
    ex_mem.rd = id_ex.rd
    ex_mem.rs1 = id_ex.rs1
    ex_mem.rs2 = id_ex.rs2
    ex_mem.imm = id_ex.imm
    ex_mem.funct3 = id_ex.funct3
    ex_mem.funct7 = id_ex.funct7
    ex_mem.control_signals = id_ex.control_signals

    ex_mem.pc = id_ex.pc

    rs1_value = rf[ex_mem.rs1] if ex_mem.rs1 != "NA" else 0
    rs2_value = rf[ex_mem.rs2] if ex_mem.rs2 != "NA" else 0

    if ex_mem.control_signals['ALUOp'] == 0b0010:  # ALU: add
        ex_mem.ALU_result = rs1_value + ex_mem.imm if ex_mem.control_signals['ALUSrc'] else rs1_value + rs2_value
    
    elif ex_mem.control_signals['ALUOp'] == 0b0001:  # ALU: OR
        ex_mem.ALU_result = rs1_value | ex_mem.imm if ex_mem.control_signals['ALUSrc'] else rs1_value | rs2_value
    
    elif ex_mem.control_signals['ALUOp'] == 0b0000:  # ALU: AND
        ex_mem.ALU_result = rs1_value & ex_mem.imm if ex_mem.control_signals['ALUSrc'] else rs1_value & rs2_value

    elif ex_mem.control_signals['ALUOp'] == 0b0110:  # ALU: sub
        ex_mem.ALU_result = rs1_value - ex_mem.imm if ex_mem.control_signals['ALUSrc'] else rs1_value - rs2_value
        ex_mem.branch_target = ex_mem.imm if ex_mem.ALU_result == 0 else 0
        ex_mem.alu_zero = 1 if ex_mem.ALU_result == 0 else 0

    Decode()

def Mem():
    global ex_mem, mem_wb, d_mem
    mem_wb.opcode = ex_mem.opcode
    mem_wb.rd = ex_mem.rd
    mem_wb.rs1 = ex_mem.rs1
    mem_wb.rs2 = ex_mem.rs2
    mem_wb.imm = ex_mem.imm
    mem_wb.funct3 = ex_mem.funct3
    mem_wb.funct7 = ex_mem.funct7
    mem_wb.ALU_result = ex_mem.ALU_result
    mem_wb.control_signals = ex_mem.control_signals

    mem_wb.pc = ex_mem.pc

    if mem_wb.control_signals['MemRead']:
        mem_wb.read_data = d_mem[mem_wb.ALU_result]

    if mem_wb.control_signals['MemWrite']:
        d_mem[mem_wb.ALU_result] = rf[ex_mem.rs2] if ex_mem.rs2 != "NA" else 0
    
    Execute()

def Writeback():
    global mem_wb, rf, total_clock_cycles

    pc1 = mem_wb.pc

    if mem_wb.control_signals['RegWrite']:
        if mem_wb.rd != "NA":
            if mem_wb.control_signals['MemtoReg']:
                rf[mem_wb.rd] = mem_wb.instruction
            else:
                rf[mem_wb.rd] = mem_wb.ALU_result

    print("rf: ", rf)
    Mem()

    # Print results for each cycle
    if mem_wb.control_signals['Branch']:
        print(f"\ntotal_clock_cycles {total_clock_cycles}:")
        print(f"pc is modified to 0x{pc1:x}")

    elif mem_wb.control_signals['MemWrite']:
        print(f"\ntotal_clock_cycles {total_clock_cycles}:")
        print(f"Memory 0x{mem_wb.ALU_result:x} is modified to 0x{mem_wb.read_data:x}")
        print(f"pc is modified to 0x{pc1:x}")

    elif mem_wb.control_signals['MemRead']:
        print(f"\ntotal_clock_cycles {total_clock_cycles}:")
        print(f"x{mem_wb.rd} is modified to 0x{mem_wb.read_data:x}")
        print(f"pc is modified to 0x{pc1:x}")

    elif mem_wb.control_signals['RegWrite'] or mem_wb.control_signals['Jump']:
        print(f"\ntotal_clock_cycles {total_clock_cycles}:")
        print(f"x{mem_wb.rd} is modified to 0x{rf[mem_wb.rd]:x}")
        print(f"pc is modified to 0x{pc1:x}")

    else:
        print(f"\ntotal_clock_cycles {total_clock_cycles}:\nNo memory operation performed.")
    
def ControlUnit(opcode, funct3, funct7):
    control_signals = {
        'RegWrite': 0,
        'Branch': 0,
        'ALUSrc': 0,
        'MemWrite': 0,
        'MemtoReg': 0,
        'MemRead': 0,
        'Jump': 0
    }
    if opcode == 0b0100011:  # sw
        control_signals['MemWrite'] = 1
        control_signals['ALUSrc'] = 1
        control_signals['MemtoReg'] = 1
        control_signals['ALUOp'] = 0b0010  # add

    elif opcode == 0b1100011:  # beq
        control_signals['Branch'] = 1
        control_signals['ALUOp'] = 0b0110  # ALU: sub

    elif opcode == 0b0000011:  # lw
        control_signals['MemRead'] = 1
        control_signals['ALUSrc'] = 1
        control_signals['RegWrite'] = 1
        control_signals['MemtoReg'] = 1
        control_signals['ALUOp'] = 0b0010  # ALU: add

    elif opcode == 0b0010011: # I-type
        control_signals['RegWrite'] = 1
        control_signals['ALUSrc'] = 1
        control_signals['MemtoReg'] = 1
        if funct3 == 0b000: # addi
            control_signals['ALUOp'] = 0b0010  # ALU: add
        elif funct3 == 0b110: # ori
            control_signals['ALUOp'] = 0b0001  # ALU: OR
        elif funct3 == 0b111: # andi
            control_signals['ALUOp'] = 0b0000  # ALU: AND

    elif opcode == 0b1100111: # jalr
        control_signals['RegWrite'] = 1
        control_signals['ALUSrc'] = 1
        control_signals['Jump'] = 1
        control_signals['MemtoReg'] = 1
        control_signals['ALUOp'] = 0b0010  # ALU: add

    elif opcode == 0b0110011:  # R-type
        control_signals['RegWrite'] = 1
        if funct7 == 0b0000000:
            if funct3 == 0b000:  # add
                control_signals['ALUOp'] = 0b0010  # ALU: add
            elif funct3 == 0b110:  # or
                control_signals['ALUOp'] = 0b0001  # ALU: OR
            elif funct3 == 0b111:  # and
                control_signals['ALUOp'] = 0b0000  # ALU: AND
        elif funct7 == 0b0100000:
            if funct3 == 0b000:  # sub
                control_signals['ALUOp'] = 0b0110  # ALU: sub

    return control_signals

def main():
    global pc, total_clock_cycles, lines

    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, 'r') as file:
        lines = file.readlines()

        Fetch()
        Decode()
        Execute()
        Mem()
        Writeback()

    print("\nProgram terminated:")
    print(f"Total execution time is {total_clock_cycles} cycles")

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