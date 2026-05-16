from arvore_ast import Num, Var, OpBinaria, Atribuicao, Bloco, If, While

class Interpretador:
    def __init__(self):
        self.tabela_simbolos = {}

    def interpretar(self, arvore):
        for no in arvore:
            self.visitar(no)

    def visitar(self, no):
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.erro_generico)
        return metodo(no)

    def erro_generico(self, no):
        raise Exception(f"Nenhum método visitar_ definido para a classe {type(no).__name__}")

    def visitar_Num(self, no):
        return no.valor

    def visitar_Var(self, no):
        nome_var = no.nome
        if nome_var not in self.tabela_simbolos:
            raise NameError(f"Erro Semântico: A variável '{nome_var}' não foi declarada.")
        return self.tabela_simbolos[nome_var]

    def visitar_OpBinaria(self, no):
        esq = self.visitar(no.esquerda)
        dir = self.visitar(no.direita)

        # Operações Matemáticas
        if no.operador == '+': return esq + dir
        elif no.operador == '-': return esq - dir
        elif no.operador == '*': return esq * dir
        elif no.operador == '/':
            if dir == 0: raise ZeroDivisionError("Divisão por zero.")
            return esq / dir
            
        # Operações Relacionais (NOVAS!)
        elif no.operador == '==': return esq == dir
        elif no.operador == '!=': return esq != dir
        elif no.operador == '<': return esq < dir
        elif no.operador == '>': return esq > dir
        elif no.operador == '<=': return esq <= dir
        elif no.operador == '>=': return esq >= dir

    def visitar_Atribuicao(self, no):
        resultado = self.visitar(no.expressao)
        self.tabela_simbolos[no.variavel.nome] = resultado

    def visitar_Bloco(self, no):
        # Executa todas as instruções dentro de { }
        for instrucao in no.instrucoes:
            self.visitar(instrucao)

    def visitar_If(self, no):
        # Se a condição for verdade, visita o bloco verdadeiro
        if self.visitar(no.condicao):
            self.visitar(no.bloco_verdadeiro)
        # Se for falsa e existir um Else, visita o bloco falso
        elif no.bloco_falso:
            self.visitar(no.bloco_falso)

    def visitar_While(self, no):
        # Continua a visitar o bloco ENQUANTO a condição for verdadeira
        while self.visitar(no.condicao):
            self.visitar(no.bloco)