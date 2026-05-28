import json

class ASTNode:
    def to_dict(self):
        raise NotImplementedError

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

class Programa(ASTNode):
    def __init__(self, funcoes):
        self.funcoes = funcoes  # Lista de Funcao

    def to_dict(self):
        return {
            "node": "Programa",
            "funcoes": [f.to_dict() for f in self.funcoes]
        }

class Funcao(ASTNode):
    def __init__(self, tipo_retorno, nome, parametros, bloco, linha):
        self.tipo_retorno = tipo_retorno
        self.nome = nome
        self.parametros = parametros  # Lista de Parametro
        self.bloco = bloco            # Bloco
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Funcao",
            "tipo_retorno": self.tipo_retorno,
            "nome": self.nome,
            "linha": self.linha,
            "parametros": [p.to_dict() for p in self.parametros],
            "bloco": self.bloco.to_dict()
        }

class Parametro(ASTNode):
    def __init__(self, tipo, nome, linha):
        self.tipo = tipo
        self.nome = nome
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Parametro",
            "tipo": self.tipo,
            "nome": self.nome,
            "linha": self.linha
        }

class Bloco(ASTNode):
    def __init__(self, declaracoes, comandos):
        self.declaracoes = declaracoes  # Lista de Declaracao
        self.comandos = comandos        # Lista de Comando

    def to_dict(self):
        return {
            "node": "Bloco",
            "declaracoes": [d.to_dict() for d in self.declaracoes],
            "comandos": [c.to_dict() for c in self.comandos]
        }

class Declaracao(ASTNode):
    def __init__(self, tipo, nome, linha):
        self.tipo = tipo
        self.nome = nome
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Declaracao",
            "tipo": self.tipo,
            "nome": self.nome,
            "linha": self.linha
        }

class Comando(ASTNode):
    pass

class Se(Comando):
    def __init__(self, condicao, entao_cmd, senao_cmd, linha):
        self.condicao = condicao      # Expr
        self.entao_cmd = entao_cmd    # Lista de Comando
        self.senao_cmd = senao_cmd    # Lista de Comando (opcional)
        self.linha = linha

    def to_dict(self):
        d = {
            "node": "Se",
            "condicao": self.condicao.to_dict(),
            "linha": self.linha,
            "entao": [c.to_dict() for c in self.entao_cmd]
        }
        if self.senao_cmd is not None:
            d["senao"] = [c.to_dict() for c in self.senao_cmd]
        return d

class Enquanto(Comando):
    def __init__(self, condicao, comandos, linha):
        self.condicao = condicao      # Expr
        self.comandos = comandos      # Lista de Comando
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Enquanto",
            "condicao": self.condicao.to_dict(),
            "linha": self.linha,
            "comandos": [c.to_dict() for c in self.comandos]
        }

class FacaEnquanto(Comando):
    def __init__(self, comandos, condicao, linha):
        self.comandos = comandos      # Lista de Comando
        self.condicao = condicao      # Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "FacaEnquanto",
            "comandos": [c.to_dict() for c in self.comandos],
            "condicao": self.condicao.to_dict(),
            "linha": self.linha
        }

class Para(Comando):
    def __init__(self, variavel, inicio, fim, comandos, linha):
        self.variavel = variavel      # str
        self.inicio = inicio          # Expr
        self.fim = fim                # Expr
        self.comandos = comandos      # Lista de Comando
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Para",
            "variavel": self.variavel,
            "inicio": self.inicio.to_dict(),
            "fim": self.fim.to_dict(),
            "linha": self.linha,
            "comandos": [c.to_dict() for c in self.comandos]
        }

class Atribuicao(Comando):
    def __init__(self, variavel, expressao, linha):
        self.variavel = variavel      # str
        self.expressao = expressao    # Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Atribuicao",
            "variavel": self.variavel,
            "expressao": self.expressao.to_dict(),
            "linha": self.linha
        }

class ChamadaFuncaoCmd(Comando):
    def __init__(self, nome, argumentos, linha):
        self.nome = nome              # str
        self.argumentos = argumentos  # Lista de Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "ChamadaFuncaoCmd",
            "nome": self.nome,
            "argumentos": [a.to_dict() for a in self.argumentos],
            "linha": self.linha
        }

class Retorne(Comando):
    def __init__(self, expressao, linha):
        self.expressao = expressao    # Expr (opcional)
        self.linha = linha

    def to_dict(self):
        d = {"node": "Retorne", "linha": self.linha}
        if self.expressao is not None:
            d["expressao"] = self.expressao.to_dict()
        return d

class Expr(ASTNode):
    pass

class BinOp(Expr):
    def __init__(self, esquerda, operador, direita, linha):
        self.esquerda = esquerda      # Expr
        self.operador = operador      # str
        self.direita = direita        # Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "BinOp",
            "esquerda": self.esquerda.to_dict(),
            "operador": self.operador,
            "direita": self.direita.to_dict(),
            "linha": self.linha
        }

class UnOp(Expr):
    def __init__(self, operador, operando, linha):
        self.operador = operador      # str
        self.operando = operando      # Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "UnOp",
            "operador": self.operador,
            "operando": self.operando.to_dict(),
            "linha": self.linha
        }

class Numero(Expr):
    def __init__(self, valor, linha):
        self.valor = valor            # str (ou int/float)
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Numero",
            "valor": self.valor,
            "linha": self.linha
        }

class Id(Expr):
    def __init__(self, nome, linha):
        self.nome = nome              # str
        self.linha = linha

    def to_dict(self):
        return {
            "node": "Id",
            "nome": self.nome,
            "linha": self.linha
        }

class ChamadaFuncaoExpr(Expr):
    def __init__(self, nome, argumentos, linha):
        self.nome = nome              # str
        self.argumentos = argumentos  # Lista de Expr
        self.linha = linha

    def to_dict(self):
        return {
            "node": "ChamadaFuncaoExpr",
            "nome": self.nome,
            "argumentos": [a.to_dict() for a in self.argumentos],
            "linha": self.linha
        }
