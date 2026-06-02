class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        
    def __repr__(self):
        return f"<{self.tipo}, '{self.valor}', Linha: {self.linha}>"

class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.pos = 0
        self.linha_atual = 1
        self.char_atual = self.codigo[0] if codigo_fonte else None

        self.reservadas = {
            'funcao': 'FUNCAO', 'vazio': 'VAZIO', 'inicio': 'INICIO', 'fim': 'FIM',
            'inteiro': 'INTEIRO', 'real': 'REAL', 'caractere': 'CARACTERE',
            'se': 'SE', 'entao': 'ENTAO', 'senao': 'SENAO', 'fim_se': 'FIM_SE',
            'enquanto': 'ENQUANTO', 'faca': 'FACA', 'fim_enquanto': 'FIM_ENQUANTO',
            'para': 'PARA', 'ate': 'ATE', 'fim_para': 'FIM_PARA',
            'retorne': 'RETORNE', 'OU': 'OU', 'E': 'E', 'NAO': 'NAO'
        }

    def avancar(self):
        if self.char_atual == '\n':
            self.linha_atual += 1
        self.pos += 1
        self.char_atual = self.codigo[self.pos] if self.pos < len(self.codigo) else None

    def proximo_token(self):
        while self.char_atual is not None:
            # 1. Ignorar espaços e quebras de linha
            if self.char_atual.isspace():
                self.avancar()
                continue

            # 2. Operador de divisão '/'
            if self.char_atual == '/':
                self.avancar()
                return Token('OP_ARITMETICO', '/', self.linha_atual)

            # 3. Identificadores e Palavras Reservadas
            if self.char_atual.isalpha() or self.char_atual == '_':
                texto = ''
                while self.char_atual is not None and (self.char_atual.isalnum() or self.char_atual == '_'):
                    texto += self.char_atual
                    self.avancar()
                tipo = self.reservadas.get(texto, 'ID')
                return Token(tipo, texto, self.linha_atual)

            # 4. Números
            if self.char_atual.isdigit():
                texto = ''
                while self.char_atual is not None and (self.char_atual.isdigit() or self.char_atual == '.'):
                    texto += self.char_atual
                    self.avancar()
                return Token('NUMERO', texto, self.linha_atual)

            # 5. Operadores Relacionais e Atribuição
            if self.char_atual in ('=', '!', '<', '>'):
                char_simbolo = self.char_atual
                self.avancar()
                if self.char_atual == '=':
                    self.avancar()
                    return Token('OP_REL', char_simbolo + '=', self.linha_atual)
                if char_simbolo == '=':
                    return Token('ATRIBUICAO', '=', self.linha_atual)
                return Token('OP_REL', char_simbolo, self.linha_atual)

            # 6. Outros Operadores Aritméticos
            if self.char_atual in ('+', '-', '*', '%'):
                char_simbolo = self.char_atual
                self.avancar()
                return Token('OP_ARITMETICO', char_simbolo, self.linha_atual)

            # 7. Delimitadores
            delimitadores = {
                '(': 'ABRE_PAR', ')': 'FECHA_PAR', 
                ';': 'PONTO_VIRGULA', ',': 'VIRGULA'
            }
            if self.char_atual in delimitadores:
                char_simbolo = self.char_atual
                tipo = delimitadores[self.char_atual]
                self.avancar()
                return Token(tipo, char_simbolo, self.linha_atual)

            raise SyntaxError(f"Erro Léxico [Linha {self.linha_atual}]: Caractere inesperado '{self.char_atual}'")

        return Token('EOF', '$', self.linha_atual)
