# Guia da Linguagem Portugol

Bem-vindo ao guia de uso da nossa linguagem Portugol! Este documento ensina como programar na linguagem, abordando desde a criação de variáveis até estruturas mais complexas como funções e laços de repetição.

A linguagem é procedural, fortemente tipada e projetada para ser lida de forma clara em português. 

---

## 1. Estrutura Básica de um Programa

Todo programa escrito nesta linguagem deve conter obrigatoriamente uma função principal chamada `principal`. Além disso, **todos os blocos de código devem ser delimitados pelas palavras `inicio` e `fim`**.

Um programa básico para imprimir algo na tela se parece com isso:

```text
funcao vazio principal()
inicio
    imprima(10);
fim
```

---

## 2. Tipos de Dados e Variáveis

A linguagem suporta três tipos de dados primitivos:
* `inteiro`: Para números sem casas decimais (Ex: `5`, `-10`).
* `real`: Para números decimais (Ex: `3.14`, `-0.5`).
* `caractere`: Para representar uma única letra, sempre entre aspas simples (Ex: `'a'`, `'B'`).

### Regra de Ouro: Declaração de Variáveis
Você deve **obrigatoriamente declarar todas as variáveis no início do bloco**, antes de tentar fazer contas ou imprimir coisas.

**Correto:**
```text
funcao vazio principal()
inicio
    inteiro idade;
    real altura;
    caractere genero;

    idade = 25;
    altura = 1.75;
    genero = 'M';

    imprima(idade);
fim
```

---

## 3. Matemática e Operadores

A linguagem suporta contas matemáticas tradicionais. As expressões respeitam as regras matemáticas padrão (multiplicação antes da adição, suporte a parênteses).

**Operadores suportados:**
* Adição (`+`) e Subtração (`-`)
* Multiplicação (`*`) e Divisão (`/`)
* Resto da Divisão (`%`)
* Negativo Unário (ex: `-5`)

```text
funcao vazio principal()
inicio
    inteiro x;
    inteiro y;
    real z;

    x = 10;
    y = -2;
    
    z = (x + y) * 2.5; 

    imprima(z);
fim
```

---

## 4. Tomada de Decisão (Se / Então)

Para executar um código apenas se uma condição for verdadeira, usamos a estrutura `se ... entao`. Caso contrário, podemos usar o `senao`.

**Operadores de Comparação:** Igual (`==`), Diferente (`!=`), Maior (`>`), Menor (`<`), Maior ou igual (`>=`), Menor ou igual (`<=`).
**Operadores Lógicos:** `E`, `OU`, `NAO`.

```text
funcao vazio principal()
inicio
    inteiro nota;
    nota = 8;

    se nota >= 7 entao
        imprima('A');
    senao
        imprima('R');
    fim_se
fim
```

---

## 5. Laços de Repetição (Loops)

Você pode repetir ações de três formas diferentes:

### A. Repetição enquanto uma condição for verdadeira (Enquanto)
Verifica a condição **antes** de executar.
```text
funcao vazio principal()
inicio
    inteiro contador;
    contador = 0;

    enquanto contador < 5 faca
        imprima(contador);
        contador = contador + 1;
    fim_enquanto
fim
```

### B. Fazer algo até a condição ser falsa (Faça...Enquanto)
Garante que o código vai rodar **pelo menos uma vez** antes de verificar a condição.
```text
funcao vazio principal()
inicio
    inteiro bateria;
    bateria = 10;

    faca
        bateria = bateria - 1;
        imprima(bateria);
    fim_faca enquanto bateria > 0 ;
fim
```

### C. Repetição Contada (Para)
Excelente para quando você sabe exatamente de onde até onde quer contar.
```text
funcao vazio principal()
inicio
    inteiro i;

    para i = 1 ate 10 faca
        imprima(i);
    fim_para
fim
```

---

## 6. Criando as Suas Próprias Funções

Seu código não precisa ficar todo dentro do `principal()`. Você pode criar funções para organizar a lógica.
As funções podem receber parâmetros (dados) e retornar resultados. Se a função não retornar nada, o tipo dela deve ser `vazio`.

```text
funcao inteiro somar(inteiro a, inteiro b)
inicio
    inteiro resultado;
    resultado = a + b;
    retorne resultado;
fim

funcao vazio principal()
inicio
    inteiro total;
    
    total = somar(10, 15);
    imprima(total);
fim
```

---

##  Como Executar o Seu Código

**Pré-requisitos:** Python 3 instalado.

O compilador lê o seu arquivo de texto (ex: `meu_codigo.ptg`) e gera um arquivo executável para a Máquina Virtual SAM (`.sam`).

Para compilar um programa, abra o terminal e digite:
```bash
python3 main.py caminho/do/arquivo.ptg
```

O compilador irá informá-lo se encontrou algum erro (seja de digitação ou de lógica, como atribuir decimal num inteiro) ou se obteve sucesso em todas as etapas de compilação.
