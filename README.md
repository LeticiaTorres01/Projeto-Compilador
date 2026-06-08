# Projeto de Compilador - Linguagem Portugol (Procedural)

Este projeto implementa um compilador completo construído do zero em Python (sem o uso de geradores automáticos como Lex ou Yacc). Ele passa por todas as fases da compilação: **Léxica, Sintática, Semântica e Geração de Código**, gerando um arquivo de linguagem Assembly projetado para uma Máquina de Pilha (SAM).

## Capacidades da Linguagem

A linguagem segue o **Paradigma Procedural**, sendo fortemente tipada e com suporte nativo a operações complexas.

### 1. Tipos Primitivos Suportados
* `inteiro`: Para números inteiros (ex: `10`, `-5`).
* `real`: Para números de ponto flutuante IEEE-754 (ex: `3.14`, `-0.5`). Suporta conversão automática de inteiro para real nas operações.
* `caractere`: Para caracteres literais simples (ex: `'a'`, `'B'`).

### 2. Operadores
* **Aritméticos:** Adição (`+`), Subtração (`-`), Multiplicação (`*`), Divisão (`/`), Resto (`%`). 
* **Unários:** Negativo (`-`), Positivo (`+`), Negação Lógica (`NAO`).
* **Relacionais:** Igualdade (`==`), Diferença (`!=`), Maior (`>`), Menor (`<`), Maior ou igual (`>=`), Menor ou igual (`<=`).
* **Lógicos:** Conjunção (`E`), Disjunção (`OU`).

### 3. Estruturas de Controle de Fluxo
A linguagem é robusta e suporta três tipos de loops nativos e condicionais compostas:
* **Decisão:** `se ... entao ... senao ... fim_se`
* **Repetição com teste no início:** `enquanto ... faca ... fim_enquanto`
* **Repetição com teste no final:** `faca ... fim_faca enquanto ... ;`
* **Repetição contada:** `para id = inicio ate fim faca ... fim_para`

### 4. Funções e Procedimentos
Suporta criação de métodos locais, passagem de parâmetros e retornos utilizando `funcao <Tipo> nome()`. Todo programa obrigatoriamente deve conter a função `funcao vazio principal()`.

---

## Como Executar o Compilador

**Pré-requisitos:** Python 3 instalado.

O compilador lê um arquivo de texto com o código-fonte `.ptg` e gera um arquivo Assembly `.sam` pronto para ser executado numa máquina virtual de pilha (SAM).

**Comando de Execução:**
```bash
python3 main.py caminho/do/arquivo.ptg
```

O compilador irá informá-lo visualmente sobre o sucesso de cada etapa:
1. Análise Léxica e Sintática
2. Análise Semântica
3. Geração de Código

O arquivo `.sam` final será salvo no mesmo diretório do arquivo original.

---

##  Exemplo de Código

```text
funcao vazio principal()
inicio
    inteiro x;
    inteiro y;
    real resultado;

    x = 10;
    y = -2;
    
    se x > 5 entao
        resultado = x / y;
        imprima(resultado);
    senao
        imprima('E');
    fim_se

    para i = 1 ate 5 faca
        imprima(i);
    fim_para
fim
```
