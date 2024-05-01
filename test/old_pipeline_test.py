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
        self.read_data = 0  # New field to hold data read from memory

if_id = PipelineRegister()
id_ex = PipelineRegister()
ex_mem = PipelineRegister()
mem_wb = PipelineRegister()

# Global variables
pc = 0
total_clock_cycles = 0
rf = [0] * 32
d_mem = [0] * (0x74 + 1)
lines = []

def Fetch():
    global if_id, pc, lines
    next_pc = pc + 4
    pc = next_pc
    if_id.instruction = lines[int(pc/4) - 1]

def Decode():
    global if_id, id_ex
    instruction = if_id.instruction
    id_ex.opcode, id_ex.rd, id_ex.rs1, id_ex.rs2, id_ex.imm, id_ex.funct3, id_ex.funct7 = decoder.decoder(instruction)
    id_ex.control_signals = ControlUnit(id_ex.opcode, id_ex.funct3, id_ex.funct7)

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

    if mem_wb.control_signals['MemRead']:
        mem_wb.read_data = d_mem[mem_wb.ALU_result]

    if mem_wb.control_signals['MemWrite']:
        d_mem[mem_wb.ALU_result] = rf[ex_mem.rs2] if ex_mem.rs2 != "NA" else 0

def Writeback():
    global mem_wb, rf, total_clock_cycles
    total_clock_cycles += 1

    if mem_wb.control_signals['RegWrite']:
        if mem_wb.rd != "NA":
            if mem_wb.control_signals['MemtoReg']:
                rf[mem_wb.rd] = mem_wb.instruction
            else:
                rf[mem_wb.rd] = mem_wb.ALU_result


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
    global pc, total_clock_cycles

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

            # Print results for each cycle
            if mem_wb.control_signals['Branch']:
                print(f"\ntotal_clock_cycles {total_clock_cycles}:")
                print(f"PC is modified to 0x{pc:x}")

            elif mem_wb.control_signals['MemWrite']:
                print(f"\ntotal_clock_cycles {total_clock_cycles}:")
                print(f"Memory 0x{mem_wb.ALU_result:x} is modified to 0x{mem_wb.read_data:x}")
                print(f"PC is modified to 0x{pc:x}")

            elif mem_wb.control_signals['MemRead']:
                print(f"\ntotal_clock_cycles {total_clock_cycles}:")
                print(f"x{mem_wb.rd} is modified to 0x{mem_wb.read_data:x}")
                print(f"PC is modified to 0x{pc:x}")

            elif mem_wb.control_signals['RegWrite'] or mem_wb.control_signals['Jump']:
                print(f"\ntotal_clock_cycles {total_clock_cycles}:")
                print(f"x{mem_wb.rd} is modified to 0x{rf[mem_wb.rd]:x}")
                print(f"PC is modified to 0x{pc:x}")

            else:
                print(f"\ntotal_clock_cycles {total_clock_cycles}:\nNo memory operation performed.")


    print("\nProgram terminated:")
    print(f"Total execution time is {total_clock_cycles} cycles")

if __name__ == "__main__":
    main()

