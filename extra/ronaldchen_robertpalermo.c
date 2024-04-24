#include <stdio.h>
#include <stdint.h>

// Function to sign-extend a 12-bit immediate value
// Ronald Chen
int32_t sign_extend_12(uint32_t imm) {
    if (imm & 0x800) { // Check if the sign bit is set
        imm |= 0xFFFFF000; // Perform sign extension
    }
    return (int32_t) imm; // Cast to signed int
}

// Function to sign-extend a 13-bit immediate value
// Ronald Chen
int32_t sign_extend_13(uint32_t imm) {
    if (imm & 0x1000) { // Check if the sign bit is set
        imm |= 0xFFFFE000; // Perform sign extension
    }
    return (int32_t) imm; // Cast to signed int
}

// Function to decode R-type instruction
// Robert Palermo
void decode_R(uint32_t instr) {
    uint32_t rd = (instr >> 7) & 0x1F;
    uint32_t rs2 = (instr >> 20) & 0x1F;
    uint32_t rs1 = (instr >> 15) & 0x1F;
    uint32_t funct3 = (instr >> 12) & 0x7;
    uint32_t funct7 = (instr >> 25) & 0x7F;

    printf("Instruction Type: R\n");
    switch (funct7){
        case 0b00000000:
            switch (funct3 | (funct7 << 3)) {
                case 0b0000000:
                    printf("Operation: add\n");
                    break;
                case 0b0000001:
                    printf("Operation: sll\n");
                    break;
                case 0b0000101:
                    printf("Operation: srl\n");
                    break;
                case 0b0000010:
                    printf("Operation: slt\n");
                    break;
                case 0b0000011:
                    printf("Operation: sltu\n");
                    break;
                case 0b0000100:
                    printf("Operation: xor\n");
                    break;
                case 0b0000110:
                    printf("Operation: or\n");
                    break;
                case 0b0000111:
                    printf("Operation: and\n");
                    break;
                default:
                    break;
            }
            break;
        case 0b0100000:
            switch (funct3) {
                case 0b000:
                    printf("Operation: sub\n");
                    break;
                case 0b101:
                    printf("Operation: sra\n");
                    break;
                default:
                    break;
            }
            break;
        default:
            break;    
    }
    printf("Rs1: x%d\n", rs1);
    printf("Rs2: x%d\n", rs2);
    printf("Rd: x%d\n", rd);
    printf("Funct3: %d\n", funct3);
    printf("Funct7: %d\n", funct7);
}

// Function to decode I-type instruction
// Ronald Chen
void decode_I(uint32_t instr) {
    uint32_t rd = (instr >> 7) & 0x1F;
    uint32_t rs1 = (instr >> 15) & 0x1F;
    uint32_t opcode = instr & 0x7F;
    int32_t imm = sign_extend_12((instr >> 20) & 0x5F); // Sign extend immediate

    printf("Instruction Type: I\n");
    switch (opcode) {
        case 0b0000011:
            switch ((instr >> 12) & 0b111){
                case 0b000:
                    printf("Operation: lb\n");
                    break;
                case 0b010:
                    printf("Operation: lw\n");
                    break;
                case 0b001:
                    printf("Operation: lh\n");
                    break;
            }
            break;
        case 0b0010011:
            switch ((instr >> 12) & 0b111) { // checks the func3
                case 0b000:
                    printf("Operation: addi\n");
                    break;
                case 0b001:
                    printf("Operation: slli\n");
                    break; 
                case 0b111:
                    printf("Operation: andi\n");
                    break;
                case 0b110:
                    printf("Operation: ori\n");
                    break;
                case 0b100:
                    printf("Operation: xori\n");
                    break;
                case 0b010:
                    printf("Operation: slti\n");
                    break;
                case 0b011:
                    printf("Operation: sltiu\n");
                    break;
                case 0b101:
                    switch (instr >> 25) { // checks the shtype
                        case 0b0000000:
                            printf("Operation: srli\n");
                            break;
                        case 0b0100000:
                            printf("Operation: srai\n");
                            break;
                        default:
                            break;
                    }
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
    }
    printf("Rs1: x%d\n", rs1);
    printf("Rd: x%d\n", rd);
    printf("Immediate: %d", imm);
    if (imm < 0 || imm > 9) {
        printf(" (or 0x%X)", imm & 0x5F);
    }
    printf("\n");
}

// Function to decode S-type instruction
// Robert Palermo
void decode_S(uint32_t instr) {
    uint32_t rs2 = (instr >> 20) & 0x1F;
    uint32_t rs1 = (instr >> 15) & 0x1F;
    uint32_t opcode = instr & 0x7F;
    int32_t imm = sign_extend_12(((instr >> 25) << 5) | ((instr >> 7) & 0x1F)); // Sign extend immediate

    printf("Instruction Type: S\n");
    switch (opcode) {
        case 0b0100011:
            switch ((instr >> 12) & 0b111) {
                case 0b000:
                    printf("Operation: sb\n");
                    break;
                case 0b001:
                    printf("Operation: sh\n");
                    break;
                case 0b010:
                    printf("Operation: sw\n");
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
    }
    printf("Rs1: x%d\n", rs1);
    printf("Rs2: x%d\n", rs2);
    printf("Immediate: %d", imm);
    if (imm < 0 || imm > 9) {
        printf(" (or 0x%X)", imm & 0xFFF);
    }
    printf("\n");
}

// Function to decode SB-type instruction
// Ronald Chen
void decode_SB(uint32_t instr) {
    uint32_t rs2 = (instr >> 20) & 0x1F;
    uint32_t rs1 = (instr >> 15) & 0x1F;
    uint32_t funct3 = (instr >> 12) & 0x7;
    int32_t imm = sign_extend_13(((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) |
                                 (((instr >> 25) & 0x3F) << 5) | (((instr >> 8) & 0xF) << 1)); // Sign extend immediate

    printf("Instruction Type: SB\n");
    switch (funct3) {
        case 0b000:
            printf("Operation: beq\n");
            break;
        case 0b101:
            printf("Operation: bge\n");
            break;
        case 0b100:
            printf("Operation: blt\n");
            break;
        case 0b001:
            printf("Operation: bne\n");
            break;
        default:
            break;
    }
    printf("Rs1: x%d\n", rs1);
    printf("Rs2: x%d\n", rs2);
    printf("Immediate: %d", imm);
    if (imm < 0 || imm > 9) {
        printf(" (or 0x%X)", imm & 0xFFF);
    }
    printf("\n");
}

// Function to decode UJ-type instruction
// Robert Palermo
void decode_UJ(uint32_t instr) {
    uint32_t rd = (instr >> 7) & 0x1F;
    uint32_t opcode = instr & 0x7F;
    int32_t imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) |
                  (((instr >> 20) & 0x1) << 11) | (((instr >> 21) & 0x3FF) << 1);

    printf("Instruction Type: UJ\n");
    switch (opcode) {
        case 0b1101111:
            printf("Operation: jal\n");
            break;
        default:
            break;
    }
    printf("Rd: x%d\n", rd);
    printf("Immediate: %d", imm);
    if (imm < 0 || imm > 9) {
        printf(" (or 0x%X)", imm & 0xFFF);
    }
    printf("\n");
}

// Robert Palermo
int main() {
    char binary[33];
    uint32_t instr = 0;

    // Prompt for input
    printf("Enter an instruction: ");
    scanf("%32s", binary);

    // Convert binary string to integer
    for (int i = 0; binary[i] != '\0'; i++) {
        if (binary[i] == '1') {
            instr |= (1 << (31 - i));
        }
    }

    // Decode based on opcode
    uint32_t opcode = instr & 0x7F;
    switch (opcode) {
        case 0b0110011: // R-type
            decode_R(instr);
            break;
        case 0b0000011: // I-type (lb, lw, lh)
            decode_I(instr);
            break;
        case 0b0010011: // I-type (andi, ori, xori, slti, sltiu, slli, srli, srai, addi)
            decode_I(instr);
            break;
        case 0b1100111: // I-type (jalr)
            decode_I(instr);
            break;
        case 0b0100011: // S-type
            decode_S(instr);
            break;
        case 0b1100011: // SB-type
            decode_SB(instr);
            break;
        case 0b1101111: // UJ-type
            decode_UJ(instr);
            break;
        default:
            break;
    }

    return 0;
}