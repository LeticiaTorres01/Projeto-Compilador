Projeto de Compiladores: Mini-Linguagem C-Target

Este projeto é um compilador completo construído do zero em Python (sem geradores automáticos como Lex/Yacc), cumprindo os requisitos de Análise Léxica, Sintática, Semântica e Geração de Código-alvo (Linguagem C).

Funcionalidades
- Tipos de Dados: Números (`float`), Textos (`Strings`), e Booleanos (`true`, `false`).
- Estruturas de Decisão: `if` e `else`.
- Estruturas de Repetição: `while`.
- Funções e Procedimentos: Declaração com `def`, passagem de parâmetros e `return`.
- Operadores Bit-a-bit: `&`, `|`, `^`, `<<`, `>>`.
- Comandos Nativos: Comando de saída `print`.
- Comentários: Suporte a `//` (linha) e `/* ... */` (múltiplas linhas).
- Análise Semântica: Verificação de declaração de variáveis e compatibilidade de tipos lógicos/matemáticos.

Como Executar o Compilador

1. Certifique-se de ter o Python 3 instalado.
2. Coloque o código-fonte que deseja compilar num ficheiro de texto (ex: `CodigoTeste.txt`).
3. No ficheiro `main.py`, certifique-se que a variável `caminho_ficheiro` aponta para o seu ficheiro de teste.
4. Execute o compilador no terminal:
   ```bash
   python main.py