class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    def __repr__(self):
        return f"<{self.tipo}, '{self.valor}'>"

class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.pos = 0
        self.char_atual = self.codigo[0] if codigo_fonte else None

        # Baseado nas regras 1 a 35 da sua gramática
        self.reservadas = {
            'funcao': 'FUNCAO', 'vazio': 'VAZIO', 'inicio': 'INICIO', 'fim': 'FIM',
            'inteiro': 'INTEIRO', 'real': 'REAL', 'caractere': 'CARACTERE',
            'se': 'SE', 'entao': 'ENTAO', 'senao': 'SENAO', 'fim_se': 'FIM_SE',
            'enquanto': 'ENQUANTO', 'faca': 'FACA', 'fim_enquanto': 'FIM_ENQUANTO',
            'para': 'PARA', 'ate': 'ATE', 'fim_para': 'FIM_PARA',
            'retorne': 'RETORNE', 'OU': 'OU', 'E': 'E', 'NAO': 'NAO'
        }

    def avancar(self):
        self.pos += 1
        self.char_atual = self.codigo[self.pos] if self.pos < len(self.codigo) else None

    def proximo_token(self):
        while self.char_atual is not None:
            
            # 1. Ignorar espaços e quebras de linha
            if self.char_atual.isspace():
                self.avancar()
                continue

            # 2. Identificadores e Palavras Reservadas (Regras 3 a 20 e 32)
            # Obs: isalnum() aceita letras e números. Adicionamos '_' para o 'fim_se'
            if self.char_atual.isalpha() or self.char_atual == '_':
                texto = ''
                while self.char_atual is not None and (self.char_atual.isalnum() or self.char_atual == '_'):
                    texto += self.char_atual
                    self.avancar()
                tipo = self.reservadas.get(texto, 'ID')
                return Token(tipo, texto)

            # 3. Números (Regra 32)
            if self.char_atual.isdigit():
                texto = ''
                while self.char_atual is not None and (self.char_atual.isdigit() or self.char_atual == '.'):
                    texto += self.char_atual
                    self.avancar()
                return Token('NUMERO', texto)

            # 4. Operadores Relacionais (Regra 27) e Atribuição (Regra 18)
            if self.char_atual in ('=', '!', '<', '>'):
                char_simbolo = self.char_atual
                self.avancar()
                if self.char_atual == '=':
                    self.avancar()
                    return Token('OP_REL', char_simbolo + '=') # ==, !=, <=, >=
                if char_simbolo == '=':
                    return Token('ATRIBUICAO', '=') # Apenas =
                return Token('OP_REL', char_simbolo) # Apenas < ou >

            # 5. Operadores Aritméticos (Regras 29 e 31)
            if self.char_atual in ('+', '-', '*', '/', '%'):
                char_simbolo = self.char_atual
                self.avancar()
                return Token('OP_ARITMETICO', char_simbolo)

            # 6. Delimitadores (Regras 3, 6, 9)
            delimitadores = {
                '(': 'ABRE_PAR', ')': 'FECHA_PAR', 
                ';': 'PONTO_VIRGULA', ',': 'VIRGULA'
            }
            if self.char_atual in delimitadores:
                char_simbolo = self.char_atual
                tipo = delimitadores[self.char_atual]
                self.avancar()
                return Token(tipo, char_simbolo)

            # Caractere não reconhecido
            raise SyntaxError(f"Erro Léxico: Caractere inesperado '{self.char_atual}'")

        # Fim do arquivo (Regra 1)
        return Token('EOF', '$')
    
codigo_teste = """
funcao vazio calcular(inteiro x) inicio
    se x >= 10 entao
        x = x + 1 ;
    fim_se
fim
"""
lexico = AnalisadorLexico(codigo_teste)

token = lexico.proximo_token()
while token.tipo != 'EOF':
    print(token)
    token = lexico.proximo_token()
print(token) # Imprime o $ final