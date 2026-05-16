class AST:
    """Classe base para todos os nós da Árvore Sintática Abstrata."""
    pass

class Num(AST):
    def __init__(self, token):
        self.valor = float(token[1]) # Converte o texto '10' para o número 10.0
        
    def __repr__(self):
        return f"Num({self.valor})"

class Var(AST):
    def __init__(self, token):
        self.nome = token[1] # Guarda o nome da variável (ex: 'taxa')
        
    def __repr__(self):
        return f"Var('{self.nome}')"

class OpBinaria(AST):
    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda
        self.operador = operador[1] # Símbolo: '+', '-', '*', '/'
        self.direita = direita
        
    def __repr__(self):
        return f"OpBinaria({self.operador}, {self.esquerda}, {self.direita})"

class Atribuicao(AST):
    def __init__(self, variavel, expressao):
        self.variavel = variavel     # Um nó do tipo Var
        self.expressao = expressao   # A conta matemática (OpBinaria ou Num)
        
    def __repr__(self):
        return f"Atribuicao({self.variavel.nome} = {self.expressao})"

class Bloco(AST):
    """Representa um bloco de instruções entre chaves { }"""
    def __init__(self, instrucoes):
        self.instrucoes = instrucoes # Uma lista de nós da AST
        
    def __repr__(self):
        return f"Bloco({len(self.instrucoes)} instrucoes)"

class If(AST):
    """Representa uma estrutura condicional If / Else"""
    def __init__(self, condicao, bloco_verdadeiro, bloco_falso=None):
        self.condicao = condicao             # A conta matemática ou relacional
        self.bloco_verdadeiro = bloco_verdadeiro # O Bloco a executar se for verdade
        self.bloco_falso = bloco_falso       # O Bloco a executar se for falso (opcional)
        
    def __repr__(self):
        tem_else = "Com Else" if self.bloco_falso else "Sem Else"
        return f"If({self.condicao} -> {tem_else})"

class While(AST):
    """Representa um ciclo While"""
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco
        
    def __repr__(self):
        return f"While({self.condicao})"
    
class Texto(AST):
    """Representa uma Constante de String, ex: "Olá" """
    def __init__(self, token):
        self.valor = token[1] # Guarda o texto incluindo as aspas
        
    def __repr__(self):
        return f"Texto({self.valor})"

class Print(AST):
    """Representa o comando de saída de dados"""
    def __init__(self, expressao):
        self.expressao = expressao # O que vai ser impresso (variável, conta, ou texto)
        
    def __repr__(self):
        return f"Print({self.expressao})"
    
class Booleano(AST):
    """Representa um valor Verdadeiro (true) ou Falso (false)"""
    def __init__(self, token):
        # Se a palavra for 'true', guarda o valor True do Python, senão guarda False
        self.valor = True if token[1] == 'true' else False
        
    def __repr__(self):
        return f"Booleano({str(self.valor).lower()})"
    
class FuncaoDecl(AST):
    """Representa: def nome(param1, param2) { ... }"""
    def __init__(self, nome, parametros, bloco):
        self.nome = nome
        self.parametros = parametros # Lista de textos com os nomes dos parâmetros
        self.bloco = bloco

class Chamada(AST):
    """Representa: nome(arg1, arg2)"""
    def __init__(self, nome, argumentos):
        self.nome = nome
        self.argumentos = argumentos # Lista de nós AST

class Return(AST):
    """Representa: return expressao;"""
    def __init__(self, expressao):
        self.expressao = expressao