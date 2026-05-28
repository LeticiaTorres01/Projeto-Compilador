import sys
import os
from lexico import AnalisadorLexico
from sintatico import AnalisadorSintatico
from semantico import AnalisadorSemantico
from gerador_codigo import GeradorCodigo

def compilar(caminho_ficheiro):
    print("========================================")
    print(" COMPILADOR PORTUGOL -> SAM")
    print(f" Arquivo: {caminho_ficheiro}")
    print("========================================\n")

    try:
        with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()

        # 1. Front-End (Léxico e Sintático)
        print("[1/3] Executando Análise Léxica e Sintática...")
        lexico = AnalisadorLexico(codigo_fonte)
        sintatico = AnalisadorSintatico(lexico)
        ast_raiz = sintatico.parse_programa()
        print("      -> Sucesso!")

        # 2. Middle-End (Semântico)
        print("[2/3] Executando Análise Semântica...")
        semantico = AnalisadorSemantico()
        semantico.visitar(ast_raiz)
        print("      -> Sucesso! Código semanticamente válido.")
        
        # 3. Back-End (Geração de Código)
        print("[3/3] Gerando Código Assembly SAM...")
        gerador = GeradorCodigo()
        codigo_sam = gerador.gerar(ast_raiz)
        
        # Define o nome do ficheiro de saída (ex: programa.ptg -> programa.sam)
        nome_base = os.path.splitext(caminho_ficheiro)[0]
        ficheiro_saida = f"{nome_base}.sam"
        
        with open(ficheiro_saida, 'w', encoding='utf-8') as f:
            f.write(codigo_sam)
            
        print(f"\n[SUCESSO] Compilação terminada! Ficheiro gerado: {ficheiro_saida}")

    except SyntaxError as e:
        print("\n[ERRO SINTÁTICO / LÉXICO]")
        print(e)
    except Exception as e:
        print("\n[ERRO DE COMPILAÇÃO]")
        print(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        compilar(sys.argv[1])
    else:
        print("Uso: python main.py <ficheiro.ptg>")
        caminho_padrao = os.path.join(os.path.dirname(__file__), "testes", "programa1.ptg")
        if os.path.exists(caminho_padrao):
            print(f"\nExecutando o teste padrão: {caminho_padrao}\n")
            compilar(caminho_padrao)
