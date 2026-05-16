from arvore_ast import Num, Var, OpBinaria, Atribuicao, Bloco, If, While, Texto, Print, Booleano, FuncaoDecl, Chamada, Return

class ErroSemantico(Exception):
    pass

class AnalisadorSemantico:
    def __init__(self):
        # A nossa Tabela de Símbolos que guarda o TIPO da variável, e não o valor.
        # Ex: {'contador': 'NUMERO', 'status': 'BOOLEANO'}
        self.tabela_tipos = {}

    def analisar(self, arvore):
        for no in arvore:
            self.visitar(no)

    def visitar(self, no):
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.erro_generico)
        return metodo(no)

    def erro_generico(self, no):
        raise Exception(f"Analisador semântico não definido para {type(no).__name__}")

    # --- REGRAS DE TIPAGEM BÁSICA ---
    def visitar_Num(self, no):
        return 'NUMERO'

    def visitar_Texto(self, no):
        return 'TEXTO'

    def visitar_Booleano(self, no):
        return 'BOOLEANO'

    def visitar_Var(self, no):
        nome_var = no.nome
        if nome_var not in self.tabela_tipos:
            raise ErroSemantico(f"A variável '{nome_var}' foi usada sem ser declarada.")
        return self.tabela_tipos[nome_var]

    # --- VERIFICAÇÃO DE OPERAÇÕES ---
    def visitar_OpBinaria(self, no):
        tipo_esq = self.visitar(no.esquerda)
        tipo_dir = self.visitar(no.direita)

        # Matemática e Bit-a-bit só funcionam com NÚMEROS
        operadores_numericos = ['+', '-', '*', '/', '<<', '>>', '&', '|', '^']
        if no.operador in operadores_numericos:
            if tipo_esq != 'NUMERO' or tipo_dir != 'NUMERO':
                raise ErroSemantico(f"Operador '{no.operador}' não suporta os tipos {tipo_esq} e {tipo_dir}.")
            return 'NUMERO'

        # Comparações (>, <, >=, <=) só funcionam com NÚMEROS
        operadores_relacionais = ['>', '<', '>=', '<=']
        if no.operador in operadores_relacionais:
            if tipo_esq != 'NUMERO' or tipo_dir != 'NUMERO':
                raise ErroSemantico(f"Operador '{no.operador}' exige dois NÚMEROS.")
            return 'BOOLEANO' # O resultado de uma comparação é sempre um Booleano

        # Igualdade (==, !=) funciona se os tipos forem iguais
        if no.operador in ['==', '!=']:
            if tipo_esq != tipo_dir:
                raise ErroSemantico(f"Não pode comparar igualdade entre {tipo_esq} e {tipo_dir}.")
            return 'BOOLEANO'

    # --- VERIFICAÇÃO DE ESTRUTURAS ---
    def visitar_Atribuicao(self, no):
        nome_var = no.variavel.nome
        tipo_expressao = self.visitar(no.expressao)
        
        # Guardamos na Tabela de Símbolos que esta variável agora tem este tipo
        self.tabela_tipos[nome_var] = tipo_expressao

    def visitar_Bloco(self, no):
        for instrucao in no.instrucoes:
            self.visitar(instrucao)

    def visitar_If(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != 'BOOLEANO':
            raise ErroSemantico(f"A condição do 'if' deve ser um BOOLEANO, mas recebeu {tipo_condicao}.")
        
        self.visitar(no.bloco_verdadeiro)
        if no.bloco_falso:
            self.visitar(no.bloco_falso)

    def visitar_While(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != 'BOOLEANO':
            raise ErroSemantico(f"A condição do 'while' deve ser um BOOLEANO, mas recebeu {tipo_condicao}.")
        self.visitar(no.bloco)

    def visitar_Print(self, no):
        # Print aceita qualquer coisa, só precisamos de visitar para garantir 
        # que as variáveis dentro dele existem.
        self.visitar(no.expressao)

    def visitar_FuncaoDecl(self, no):
        # Para simplificar, assumimos que os parâmetros são NUMEROS
        for param in no.parametros:
            self.tabela_tipos[param] = 'NUMERO'
        self.visitar(no.bloco)

    def visitar_Chamada(self, no):
        for arg in no.argumentos:
            self.visitar(arg)
        return 'NUMERO' # Assumimos que funções retornam números

    def visitar_Return(self, no):
        self.visitar(no.expressao)