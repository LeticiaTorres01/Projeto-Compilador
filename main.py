from scanner import analisar_lexico
from parser_sintatico import Parser
from interpretador import Interpretador 
from gerador_codigo import GeradorCodigo
from analisador_semantico import AnalisadorSemantico, ErroSemantico

def main():
    caminho_ficheiro = 'CodigoTeste.txt'
    
    try:
        with open(caminho_ficheiro, 'r', encoding='utf-8') as ficheiro:
            codigo = ficheiro.read()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{caminho_ficheiro}' não foi encontrado.")
        return

    print("--- 1. ANÁLISE LÉXICA ---")
    try:
        lista_tokens = analisar_lexico(codigo)
    except RuntimeError as erro:
        print(f"\n[ERRO LÉXICO] {erro}")
        return 

    print("\n--- 2. ANÁLISE SINTÁTICA E AST ---")
    try:
        parser = Parser(lista_tokens)
        arvore = parser.iniciar()
    except SyntaxError as erro:
        print(f"\n[ERRO SINTÁTICO] {erro}")
        return
    
    # --- NOVA FASE 2.5: ANÁLISE SEMÂNTICA ---
    print("\n--- 2.5 ANÁLISE SEMÂNTICA ---")
    try:
        analisador = AnalisadorSemantico()
        analisador.analisar(arvore)
        print("Semântica validada: Tipos compatíveis e variáveis declaradas.")
    except ErroSemantico as erro:
        print(f"\n[ERRO SEMÂNTICO] {erro}")
        return # Para a compilação aqui!

    # --- NOVA FASE 3: GERAÇÃO DE CÓDIGO (BACK-END) ---
    print("\n--- 3. GERAÇÃO DE CÓDIGO (C) ---")
    try:
        gerador = GeradorCodigo()
        codigo_c = gerador.gerar(arvore)
        
        print(codigo_c) # Mostra o código gerado no ecrã
        
        # Cria fisicamente o ficheiro final compilado
        nome_ficheiro_saida = "saida.c"
        with open(nome_ficheiro_saida, "w", encoding="utf-8") as ficheiro_saida:
            ficheiro_saida.write(codigo_c)
            
        print(f"\n[SUCESSO] Compilação terminada! O ficheiro '{nome_ficheiro_saida}' foi gerado na sua pasta.")
            
    except Exception as erro:
        print(f"\n[ERRO NA GERAÇÃO DE CÓDIGO] {erro}")

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()