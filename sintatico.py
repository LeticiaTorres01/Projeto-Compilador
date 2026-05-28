from lexico import Token, AnalisadorLexico
from ast_nodes import (
    Programa, Funcao, Parametro, Bloco, Declaracao,
    Se, Enquanto, FacaEnquanto, Para, Atribuicao, ChamadaFuncaoCmd, Retorne,
    BinOp, UnOp, Numero, Id, ChamadaFuncaoExpr
)

class AnalisadorSintatico:
    def __init__(self, lexico):
        self.lexico = lexico
        self.token_atual = self.lexico.proximo_token()

    def erro(self, esperado):
        linha = self.token_atual.linha
        raise SyntaxError(f"Erro Sintático [Linha {linha}]: Esperado '{esperado}', mas encontrado '{self.token_atual.tipo}' ('{self.token_atual.valor}')")

    def match(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado:
            self.token_atual = self.lexico.proximo_token()
        else:
            self.erro(tipo_esperado)

    # 1 - <Programa> ::= <ListaFuncoes> $
    def parse_programa(self):
        funcoes = self.parse_lista_funcoes()
        self.match('EOF')
        return Programa(funcoes)

    # 2 - <ListaFuncoes> ::= <Funcao> <ListaFuncoes> | epsilon
    def parse_lista_funcoes(self):
        if self.token_atual.tipo == 'FUNCAO':
            funcao = self.parse_funcao()
            resto = self.parse_lista_funcoes()
            return [funcao] + resto
        else:
            return []

    # 3 - <Funcao> ::= funcao <TipoRetorno> id ( <Parametros> ) <Bloco>
    def parse_funcao(self):
        linha = self.token_atual.linha
        self.match('FUNCAO')
        tipo_retorno = self.parse_tipo_retorno()
        nome = self.token_atual.valor
        self.match('ID')
        self.match('ABRE_PAR')
        parametros = self.parse_parametros()
        self.match('FECHA_PAR')
        bloco = self.parse_bloco()
        return Funcao(tipo_retorno, nome, parametros, bloco, linha)

    # 4 - <TipoRetorno> ::= <Tipo> | vazio
    def parse_tipo_retorno(self):
        if self.token_atual.tipo == 'VAZIO':
            self.match('VAZIO')
            return 'vazio'
        elif self.token_atual.tipo in ['INTEIRO', 'REAL', 'CARACTERE']:
            return self.parse_tipo()
        else:
            self.erro("Tipo ou 'vazio'")

    # 5 - <Parametros> ::= <Tipo> id <RestoParametros> | epsilon
    def parse_parametros(self):
        if self.token_atual.tipo in ['INTEIRO', 'REAL', 'CARACTERE']:
            tipo = self.parse_tipo()
            linha = self.token_atual.linha
            nome = self.token_atual.valor
            self.match('ID')
            resto = self.parse_resto_parametros()
            return [Parametro(tipo, nome, linha)] + resto
        else:
            return []

    # 6 - <RestoParametros> ::= , <Tipo> id <RestoParametros> | epsilon
    def parse_resto_parametros(self):
        if self.token_atual.tipo == 'VIRGULA':
            self.match('VIRGULA')
            tipo = self.parse_tipo()
            linha = self.token_atual.linha
            nome = self.token_atual.valor
            self.match('ID')
            resto = self.parse_resto_parametros()
            return [Parametro(tipo, nome, linha)] + resto
        else:
            return []

    # 7 - <Bloco> ::= inicio <ListaDeclaracoes> <ListaComandos> fim
    def parse_bloco(self):
        self.match('INICIO')
        declaracoes = self.parse_lista_declaracoes()
        comandos = self.parse_lista_comandos()
        self.match('FIM')
        return Bloco(declaracoes, comandos)

    # 8 - <ListaDeclaracoes> ::= <Declaracao> <ListaDeclaracoes> | epsilon
    def parse_lista_declaracoes(self):
        if self.token_atual.tipo in ['INTEIRO', 'REAL', 'CARACTERE']:
            declaracao = self.parse_declaracao()
            resto = self.parse_lista_declaracoes()
            return [declaracao] + resto
        else:
            return []

    # 9 - <Declaracao> ::= <Tipo> id ;
    def parse_declaracao(self):
        tipo = self.parse_tipo()
        linha = self.token_atual.linha
        nome = self.token_atual.valor
        self.match('ID')
        self.match('PONTO_VIRGULA')
        return Declaracao(tipo, nome, linha)

    # 10 - <Tipo> ::= inteiro | real | caractere
    def parse_tipo(self):
        tipo_str = self.token_atual.valor
        if self.token_atual.tipo == 'INTEIRO':
            self.match('INTEIRO')
        elif self.token_atual.tipo == 'REAL':
            self.match('REAL')
        elif self.token_atual.tipo == 'CARACTERE':
            self.match('CARACTERE')
        else:
            self.erro("Tipo primitivo")
        return tipo_str

    # 11 - <ListaComandos> ::= <Comando> <ListaComandos> | epsilon
    def parse_lista_comandos(self):
        predict_comando = ['SE', 'ENQUANTO', 'FACA', 'PARA', 'ID', 'RETORNE']
        if self.token_atual.tipo in predict_comando:
            comando = self.parse_comando()
            resto = self.parse_lista_comandos()
            return [comando] + resto
        else:
            return []

    # 12 a 19 - <Comando>
    def parse_comando(self):
        if self.token_atual.tipo == 'SE':
            linha = self.token_atual.linha
            self.match('SE')
            condicao = self.parse_expr()
            self.match('ENTAO')
            entao_cmd = self.parse_lista_comandos()
            senao_cmd = self.parse_resto_se()
            return Se(condicao, entao_cmd, senao_cmd, linha)

        elif self.token_atual.tipo == 'ENQUANTO':
            linha = self.token_atual.linha
            self.match('ENQUANTO')
            condicao = self.parse_expr()
            self.match('FACA')
            comandos = self.parse_lista_comandos()
            self.match('FIM_ENQUANTO')
            return Enquanto(condicao, comandos, linha)

        elif self.token_atual.tipo == 'FACA':
            linha = self.token_atual.linha
            self.match('FACA')
            comandos = self.parse_lista_comandos()
            self.match('ENQUANTO')
            condicao = self.parse_expr()
            self.match('PONTO_VIRGULA')
            return FacaEnquanto(comandos, condicao, linha)

        elif self.token_atual.tipo == 'PARA':
            linha = self.token_atual.linha
            self.match('PARA')
            var_name = self.token_atual.valor
            self.match('ID')
            self.match('ATRIBUICAO')
            inicio = self.parse_expr()
            self.match('ATE')
            fim = self.parse_expr()
            self.match('FACA')
            comandos = self.parse_lista_comandos()
            self.match('FIM_PARA')
            return Para(var_name, inicio, fim, comandos, linha)

        elif self.token_atual.tipo == 'ID':
            linha = self.token_atual.linha
            id_name = self.token_atual.valor
            self.match('ID')
            return self.parse_resto_id_comando(id_name, linha)

        elif self.token_atual.tipo == 'RETORNE':
            linha = self.token_atual.linha
            self.match('RETORNE')
            expressao = self.parse_retorno_opcional()
            self.match('PONTO_VIRGULA')
            return Retorne(expressao, linha)
        else:
            self.erro("Comando válido")

    # 13 - <RestoSe> ::= senao <ListaComandos> fim_se | fim_se
    def parse_resto_se(self):
        if self.token_atual.tipo == 'SENAO':
            self.match('SENAO')
            comandos = self.parse_lista_comandos()
            self.match('FIM_SE')
            return comandos
        elif self.token_atual.tipo == 'FIM_SE':
            self.match('FIM_SE')
            return None
        else:
            self.erro("'senao' ou 'fim_se'")

    # 18 - <RestoIdComando> ::= = <Expr> ; | ( <ListaArgumentos> ) ;
    def parse_resto_id_comando(self, id_name, linha):
        if self.token_atual.tipo == 'ATRIBUICAO':
            self.match('ATRIBUICAO')
            expr = self.parse_expr()
            self.match('PONTO_VIRGULA')
            return Atribuicao(id_name, expr, linha)
        elif self.token_atual.tipo == 'ABRE_PAR':
            self.match('ABRE_PAR')
            args = self.parse_lista_argumentos()
            self.match('FECHA_PAR')
            self.match('PONTO_VIRGULA')
            return ChamadaFuncaoCmd(id_name, args, linha)
        else:
            self.erro("'=' ou '('")

    # 20 - <RetornoOpcional> ::= <Expr> | epsilon
    def parse_retorno_opcional(self):
        predict_expr = ['ID', 'NUMERO', 'ABRE_PAR', 'NAO']
        if self.token_atual.tipo in predict_expr:
            return self.parse_expr()
        else:
            return None

    # 21 - <Expr> ::= <ExprE> <RestoOu>
    def parse_expr(self):
        lhs = self.parse_expr_e()
        return self.parse_resto_ou(lhs)

    # 22 - <RestoOu> ::= OU <ExprE> <RestoOu> | epsilon
    def parse_resto_ou(self, lhs):
        if self.token_atual.tipo == 'OU':
            linha = self.token_atual.linha
            op = self.token_atual.valor
            self.match('OU')
            rhs = self.parse_expr_e()
            node = BinOp(lhs, op, rhs, linha)
            return self.parse_resto_ou(node)
        else:
            return lhs

    # 23 - <ExprE> ::= <ExprRelacional> <RestoE>
    def parse_expr_e(self):
        lhs = self.parse_expr_relacional()
        return self.parse_resto_e(lhs)

    # 24 - <RestoE> ::= E <ExprRelacional> <RestoE> | epsilon
    def parse_resto_e(self, lhs):
        if self.token_atual.tipo == 'E':
            linha = self.token_atual.linha
            op = self.token_atual.valor
            self.match('E')
            rhs = self.parse_expr_relacional()
            node = BinOp(lhs, op, rhs, linha)
            return self.parse_resto_e(node)
        else:
            return lhs

    # 25 - <ExprRelacional> ::= <ExprAritmetica> <RestoRelacional>
    def parse_expr_relacional(self):
        lhs = self.parse_expr_aritmetica()
        return self.parse_resto_relacional(lhs)

    # 26 - <RestoRelacional> ::= <OpRel> <ExprAritmetica> | epsilon
    def parse_resto_relacional(self, lhs):
        if self.token_atual.tipo == 'OP_REL':
            linha = self.token_atual.linha
            op = self.token_atual.valor
            self.match('OP_REL')
            rhs = self.parse_expr_aritmetica()
            return BinOp(lhs, op, rhs, linha)
        else:
            return lhs

    # 28 - <ExprAritmetica> ::= <Termo> <RestoAritmetico>
    def parse_expr_aritmetica(self):
        lhs = self.parse_termo()
        return self.parse_resto_aritmetico(lhs)

    # 29 - <RestoAritmetico> ::= + <Termo> <RestoAritmetico> | - <Termo> <RestoAritmetico> | epsilon
    def parse_resto_aritmetico(self, lhs):
        if self.token_atual.tipo == 'OP_ARITMETICO' and self.token_atual.valor in ['+', '-']:
            linha = self.token_atual.linha
            op = self.token_atual.valor
            self.match('OP_ARITMETICO')
            rhs = self.parse_termo()
            node = BinOp(lhs, op, rhs, linha)
            return self.parse_resto_aritmetico(node)
        else:
            return lhs

    # 30 - <Termo> ::= <Fator> <RestoTermo>
    def parse_termo(self):
        lhs = self.parse_fator()
        return self.parse_resto_termo(lhs)

    # 31 - <RestoTermo> ::= * <Fator> <RestoTermo> | / <Fator> <RestoTermo> | % <Fator> <RestoTermo> | epsilon
    def parse_resto_termo(self, lhs):
        if self.token_atual.tipo == 'OP_ARITMETICO' and self.token_atual.valor in ['*', '/', '%']:
            linha = self.token_atual.linha
            op = self.token_atual.valor
            self.match('OP_ARITMETICO')
            rhs = self.parse_fator()
            node = BinOp(lhs, op, rhs, linha)
            return self.parse_resto_termo(node)
        else:
            return lhs

    # 32 - <Fator> ::= id <RestoIdFator> | numero | ( <Expr> ) | NAO <Fator>
    def parse_fator(self):
        if self.token_atual.tipo == 'ID':
            linha = self.token_atual.linha
            id_name = self.token_atual.valor
            self.match('ID')
            return self.parse_resto_id_fator(id_name, linha)
        elif self.token_atual.tipo == 'NUMERO':
            linha = self.token_atual.linha
            val = self.token_atual.valor
            self.match('NUMERO')
            return Numero(val, linha)
        elif self.token_atual.tipo == 'ABRE_PAR':
            self.match('ABRE_PAR')
            expr = self.parse_expr()
            self.match('FECHA_PAR')
            return expr
        elif self.token_atual.tipo == 'NAO':
            linha = self.token_atual.linha
            self.match('NAO')
            fator = self.parse_fator()
            return UnOp('NAO', fator, linha)
        else:
            self.erro("Fator válido (ID, Número, '(' ou 'NAO')")

    # 33 - <RestoIdFator> ::= ( <ListaArgumentos> ) | epsilon
    def parse_resto_id_fator(self, id_name, linha):
        if self.token_atual.tipo == 'ABRE_PAR':
            self.match('ABRE_PAR')
            args = self.parse_lista_argumentos()
            self.match('FECHA_PAR')
            return ChamadaFuncaoExpr(id_name, args, linha)
        else:
            return Id(id_name, linha)

    # 34 - <ListaArgumentos> ::= <Expr> <RestoArgumentos> | epsilon
    def parse_lista_argumentos(self):
        predict_expr = ['ID', 'NUMERO', 'ABRE_PAR', 'NAO']
        if self.token_atual.tipo in predict_expr:
            expr = self.parse_expr()
            resto = self.parse_resto_argumentos()
            return [expr] + resto
        else:
            return []

    # 35 - <RestoArgumentos> ::= , <Expr> <RestoArgumentos> | epsilon
    def parse_resto_arguments(self):
        # Note: the python name is parse_resto_argumentos to match original taaa
        return self.parse_resto_argumentos()

    def parse_resto_argumentos(self):
        if self.token_atual.tipo == 'VIRGULA':
            self.match('VIRGULA')
            expr = self.parse_expr()
            resto = self.parse_resto_argumentos()
            return [expr] + resto
        else:
            return []
