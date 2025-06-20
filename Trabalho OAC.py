import os
import re

PASTA_ENTRADA = "arquivos_asm_para_traducao"
PASTA_SAIDA = "arquivos_traduzidos"

TIPO_OPERACAO = {
    "lb": "I", "lh": "I", "lw": "I", "addi": "I", "andi": "I", "ori": "I",
    "sb": "S", "sh": "S", "sw": "S",
    "add": "R", "sub": "R", "and": "R", "or": "R", "xor": "R", "sll": "R", "srl": "R",
    "bne": "SB", "beq": "SB"
}

OPCODE = {
    "lb": "0000011", "lh": "0000011", "lw": "0000011", "sb": "0100011",
    "sh": "0100011", "sw": "0100011", "add": "0110011", "sub": "0110011",
    "and": "0110011", "or": "0110011", "xor": "0110011", "sll": "0110011",
    "srl": "0110011", "addi": "0010011", "andi": "0010011", "ori": "0010011",
    "bne": "1100011", "beq": "1100011"
}

FUNCT3 = {
    "lb": "000", "lh": "001", "lw": "010", "sb": "000", "sh": "001",
    "sw": "010", "add": "000", "sub": "000", "and": "111", "or": "110",
    "xor": "100", "sll": "001", "srl": "101", "addi": "000", "andi": "111",
    "ori": "110", "bne": "001", "beq": "000"
}

FUNCT7 = {
    "add": "0000000", "sub": "0100000", "and": "0000000", "or": "0000000",
    "xor": "0000000", "sll": "0000000", "srl": "0000000"
}

REGISTRADORES = {f'x{i}': i for i in range(32)}
REGISTRADORES.update({
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4, 't0': 5, 't1': 6, 't2': 7,
    's0': 8, 'fp': 8, 's1': 9, 'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14,
    'a5': 15, 'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21,
    's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27, 't3': 28,
    't4': 29, 't5': 30, 't6': 31
})

def decimal_para_binario(decimal, qntde_bits):
    if decimal >= 0:
        return format(decimal, '0' + str(qntde_bits) + 'b')
    else:
        return format((1 << qntde_bits) + decimal, '0' + str(qntde_bits) + 'b')

def traduzir_linha(linha_asm):
    linha_limpa = linha_asm.strip().replace(',', '')
    partes = linha_limpa.split()

    if not partes:
        return ""

    instrucao = partes[0]
    operandos = partes[1:]
    
    tipo = TIPO_OPERACAO.get(instrucao)
    if tipo is None:
        return f"# ERRO: Instrução '{instrucao}' desconhecida.\n"

    linha_binaria_completa = ""

    if tipo == 'R':
        rd = decimal_para_binario(REGISTRADORES[operandos[0]], 5)
        rs1 = decimal_para_binario(REGISTRADORES[operandos[1]], 5)
        rs2 = decimal_para_binario(REGISTRADORES[operandos[2]], 5)
        linha_binaria_completa = FUNCT7[instrucao] + rs2 + rs1 + FUNCT3[instrucao] + rd + OPCODE[instrucao]

    elif tipo == 'I':
        rd = decimal_para_binario(REGISTRADORES[operandos[0]], 5)
        if '(' in operandos[1]:
            match = re.match(r'(-?\d+)\((.+)\)', operandos[1])
            imediato_str, rs1_str = match.groups()
            imediato = decimal_para_binario(int(imediato_str), 12)
            rs1 = decimal_para_binario(REGISTRADORES[rs1_str], 5)
        else:
            rs1 = decimal_para_binario(REGISTRADORES[operandos[1]], 5)
            imediato = decimal_para_binario(int(operandos[2]), 12)
        linha_binaria_completa = imediato + rs1 + FUNCT3[instrucao] + rd + OPCODE[instrucao]

    elif tipo == 'S':
        rs2_str = operandos[0]
        match = re.match(r'(-?\d+)\((.+)\)', operandos[1])
        imediato_str, rs1_str = match.groups()

        imediato_bin = decimal_para_binario(int(imediato_str), 12)
        imm11_5 = imediato_bin[0:7]
        imm4_0 = imediato_bin[7:12]

        rs1 = decimal_para_binario(REGISTRADORES[rs1_str], 5)
        rs2 = decimal_para_binario(REGISTRADORES[rs2_str], 5)
        
        linha_binaria_completa = imm11_5 + rs2 + rs1 + FUNCT3[instrucao] + imm4_0 + OPCODE[instrucao]

    elif tipo == 'SB':
        rs1 = decimal_para_binario(REGISTRADORES[operandos[0]], 5)
        rs2 = decimal_para_binario(REGISTRADORES[operandos[1]], 5)
        imediato_bin = decimal_para_binario(int(operandos[2]), 13)
        
        imm12 = imediato_bin[0]
        imm10_5 = imediato_bin[2:8]
        imm4_1 = imediato_bin[8:12]
        imm11 = imediato_bin[1]
        
        linha_binaria_completa = imm12 + imm10_5 + rs2 + rs1 + FUNCT3[instrucao] + imm4_1 + imm11 + OPCODE[instrucao]

    return linha_binaria_completa + '\n'

def main():
    if not os.path.exists(PASTA_ENTRADA):
        print(f"ERRO: A pasta de entrada '{PASTA_ENTRADA}' não foi encontrada.")
        print("Por favor, crie a pasta e coloque seus arquivos .asm dentro dela.")
        return

    os.makedirs(PASTA_SAIDA, exist_ok=True)
    
    arquivos_asm_para_traducao = os.listdir(PASTA_ENTRADA)
    for arquivo in arquivos_asm_para_traducao:
        if arquivo.endswith('.asm'):
            entrada = os.path.join(PASTA_ENTRADA, arquivo)
            arquivo_novo = arquivo.replace('.asm', '.txt')
            saida = os.path.join(PASTA_SAIDA, arquivo_novo)

            print(f"Traduzindo '{entrada}' para '{saida}'...")
            
            with open(entrada, 'r') as f_entrada, open(saida, 'w') as f_saida:
                for linha_asm in f_entrada:
                    linha_traduzida = traduzir_linha(linha_asm)
                    f_saida.write(linha_traduzida)
            print("Tradução concluída.")

if __name__ == "__main__":
    main()