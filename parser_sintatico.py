from arvore_ast import Num, Var, OpBinaria, Atribuicao, Bloco, If, While, Texto, Print, Booleano, FuncaoDecl, Chamada, Return

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0 
        self.token_atual = self.tokens[self.pos] if self.tokens else None

    def avancar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
        else:
            self.token_atual = None

    def comer(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.avancar()
        else:
            encontrado = self.token_atual[0] if self.token_atual else "FIM"
            raise SyntaxError(f"Erro Sintático: Esperado '{tipo_esperado}', mas encontrado '{encontrado}'")

    # --- REGRAS DO PARSER ---

    def programa(self):
        nos = []
        while self.token_atual is not None:
            # Se a linha começa com 'def', é uma função. Senão, é uma instrução normal.
            if self.token_atual[0] == 'DEF':
                nos.append(self.cmd_def())
            else:
                nos.append(self.instrucao())
        return nos

    def instrucao(self):
        if self.token_atual is None: return None
        if self.token_atual[0] == 'IF': return self.cmd_if()
        elif self.token_atual[0] == 'WHILE': return self.cmd_while()
        elif self.token_atual[0] == 'PRINT': return self.cmd_print()
        elif self.token_atual[0] == 'RETURN': # <--- NOVO
            self.comer('RETURN')
            expr = self.expressao_relacional()
            self.comer('SEMI')
            return Return(expr)
        elif self.token_atual[0] == 'ID': return self.atribuicao()
        else: raise SyntaxError(f"Comando inválido iniciado com: '{self.token_atual[1]}'")

    def cmd_def(self):
        """Regra: def ID '(' [ID (',' ID)*] ')' Bloco"""
        self.comer('DEF')
        nome_funcao = self.token_atual[1]
        self.comer('ID')
        self.comer('LPAREN')
        
        parametros = []
        if self.token_atual[0] == 'ID':
            parametros.append(self.token_atual[1])
            self.comer('ID')
            while self.token_atual[0] == 'COMMA':
                self.comer('COMMA')
                parametros.append(self.token_atual[1])
                self.comer('ID')
                
        self.comer('RPAREN')
        bloco = self.bloco()
        return FuncaoDecl(nome_funcao, parametros, bloco)

    def bloco(self):
        """Regra: '{' instrucao* '}'"""
        self.comer('LBRACE')
        instrucoes = []
        while self.token_atual and self.token_atual[0] != 'RBRACE':
            instrucoes.append(self.instrucao())
        self.comer('RBRACE')
        return Bloco(instrucoes)

    def cmd_print(self):
        """Regra: print '(' expressao ')' ';' """
        self.comer('PRINT')
        self.comer('LPAREN')
        no = self.expressao_relacional()
        self.comer('RPAREN')
        self.comer('SEMI')
        return Print(no)

    def cmd_if(self):
        """Regra para o IF e opcionalmente o ELSE."""
        self.comer('IF')
        self.comer('LPAREN')
        condicao = self.expressao_relacional()
        self.comer('RPAREN')
        
        bloco_verdadeiro = self.bloco()
        bloco_falso = None
        
        if self.token_atual and self.token_atual[0] == 'ELSE':
            self.comer('ELSE')
            bloco_falso = self.bloco()
            
        return If(condicao, bloco_verdadeiro, bloco_falso)

    def cmd_while(self):
        """Regra para o loop WHILE."""
        self.comer('WHILE')
        self.comer('LPAREN')
        condicao = self.expressao_relacional()
        self.comer('RPAREN')
        bloco = self.bloco()
        return While(condicao, bloco)

    def atribuicao(self):
        token_var = self.token_atual
        self.comer('ID')
        self.comer('ASSIGN')
        no_expressao = self.expressao_relacional()
        self.comer('SEMI')
        return Atribuicao(Var(token_var), no_expressao)

    def expressao_relacional(self):
        no = self.expressao_bitwise() # <--- ALTERADO
        if self.token_atual and self.token_atual[0] == 'RELOP':
            token_op = self.token_atual
            self.comer('RELOP')
            no = OpBinaria(esquerda=no, operador=token_op, direita=self.expressao_bitwise()) # <--- ALTERADO
        return no
    
    def expressao_bitwise(self):
        """Resolve operadores binários (&, |, ^, <<, >>)"""
        no = self.expressao()
        while self.token_atual and self.token_atual[0] == 'BITOP':
            token_op = self.token_atual
            self.comer('BITOP')
            no = OpBinaria(esquerda=no, operador=token_op, direita=self.expressao())
        return no

    def expressao(self):
        no = self.termo()
        while self.token_atual and self.token_atual[0] == 'OP' and self.token_atual[1] in ('+', '-'):
            token_op = self.token_atual
            self.comer('OP')
            no = OpBinaria(esquerda=no, operador=token_op, direita=self.termo())
        return no

    def termo(self):
        no = self.fator()
        while self.token_atual and self.token_atual[0] == 'OP' and self.token_atual[1] in ('*', '/'):
            token_op = self.token_atual
            self.comer('OP')
            no = OpBinaria(esquerda=no, operador=token_op, direita=self.fator())
        return no

    def fator(self):
        token = self.token_atual
        if token is None: raise SyntaxError("Fim de arquivo inesperado.")
            
        if token[0] == 'NUM':
            self.comer('NUM')
            return Num(token)
        elif token[0] == 'STRING':
            self.comer('STRING')
            return Texto(token)
        elif token[0] in ('TRUE', 'FALSE'):
            tipo = token[0]
            self.comer(tipo)
            return Booleano(token)
        elif token[0] == 'ID':
            nome_var = token[1]
            self.comer('ID')
            
            # --- NOVO: Verifica se há parênteses após o ID (Chamada de Função) ---
            if self.token_atual and self.token_atual[0] == 'LPAREN':
                self.comer('LPAREN')
                argumentos = []
                if self.token_atual[0] != 'RPAREN':
                    argumentos.append(self.expressao_relacional())
                    while self.token_atual[0] == 'COMMA':
                        self.comer('COMMA')
                        argumentos.append(self.expressao_relacional())
                self.comer('RPAREN')
                return Chamada(nome_var, argumentos)
            # ----------------------------------------------------------------------
            else:
                return Var(token)
        elif token[0] == 'LPAREN':
            self.comer('LPAREN')
            no = self.expressao()
            self.comer('RPAREN')
            return no
        else:
            raise SyntaxError(f"Token inválido: '{token[1]}'")

    def iniciar(self):
        return self.programa()