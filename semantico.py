from ast_nodes import *

class TabelaSimbolos:
    def __init__(self):
        # Uma pilha de escopos (dicionários).
        # A posição 0 é o escopo global.
        self.escopos = [{}]

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()

    def declarar(self, nome, tipo, linha):
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:
            raise Exception(f"Erro Semântico [Linha {linha}]: A variável ou função '{nome}' já foi declarada anteriormente neste escopo.")
        escopo_atual[nome] = tipo

    def buscar(self, nome, linha):
        # Busca do escopo mais interno (local) para o mais externo (global)
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise Exception(f"Erro Semântico [Linha {linha}]: Variável ou função '{nome}' não declarada.")

class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()

    def visitar(self, no):
        if no is None:
            return None
        # Se for uma lista de nós, visita cada um individualmente
        if isinstance(no, list):
            for item in no:
                self.visitar(item)
            return None
            
        nome_metodo = f'visitar_{type(no).__name__}'
        visitante = getattr(self, nome_metodo, self.erro_generico)
        return visitante(no)

    def erro_generico(self, no):
        raise Exception(f"Semântica: Nenhum método visitar_{type(no).__name__} definido.")

    # ==========================================
    # Regras de Visita (Traversal)
    # ==========================================

    def visitar_Programa(self, no):
        # Registramos primeiro todas as funções no escopo global para permitir chamadas entre elas
        for func in no.funcoes:
            # O tipo de retorno 'vazio' ficará como 'VAZIO' ou o respectivo tipo.
            self.tabela.declarar(func.nome, func.tipo_retorno.upper(), func.linha)
        # Depois visitamos cada função para validar o seu conteúdo
        self.visitar(no.funcoes)

    def visitar_Funcao(self, no):
        self.tabela.entrar_escopo()
        # Regista os parâmetros no escopo da função
        self.visitar(no.parametros)
        # Valida o bloco de código internamente
        self.visitar(no.bloco)
        self.tabela.sair_escopo()

    def visitar_Parametro(self, no):
        self.tabela.declarar(no.nome, no.tipo.upper(), no.linha)

    def visitar_Bloco(self, no):
        self.visitar(no.declaracoes)
        self.visitar(no.comandos)

    def visitar_Declaracao(self, no):
        # Transforma para uppercase para padronizar com INTEIRO, REAL, etc
        self.tabela.declarar(no.nome, no.tipo.upper(), no.linha)

    def visitar_Se(self, no):
        self.visitar(no.condicao)
        self.visitar(no.entao_cmd)
        if no.senao_cmd:
            self.visitar(no.senao_cmd)

    def visitar_Enquanto(self, no):
        self.visitar(no.condicao)
        self.visitar(no.comandos)

    def visitar_FacaEnquanto(self, no):
        self.visitar(no.comandos)
        self.visitar(no.condicao)

    def visitar_Para(self, no):
        # Verifica se a variável do 'para' existe e é inteira
        tipo_var = self.tabela.buscar(no.variavel, no.linha)
        if tipo_var != 'INTEIRO':
            raise Exception(f"Erro Semântico [Linha {no.linha}]: Variável de controle do laço 'para' ({no.variavel}) deve ser do tipo 'INTEIRO'.")
        
        tipo_inicio = self.visitar(no.inicio)
        tipo_fim = self.visitar(no.fim)
        
        if tipo_inicio != 'INTEIRO' or tipo_fim != 'INTEIRO':
            raise Exception(f"Erro Semântico [Linha {no.linha}]: Os limites do laço 'para' devem resultar no tipo 'INTEIRO'.")
            
        self.visitar(no.comandos)

    def visitar_Atribuicao(self, no):
        tipo_esq = self.tabela.buscar(no.variavel, no.linha)
        tipo_dir = self.visitar(no.expressao)
        
        if tipo_esq != tipo_dir:
            # Tolerância: promove INTEIRO para REAL silenciosamente.
            if tipo_esq == 'REAL' and tipo_dir == 'INTEIRO':
                pass 
            else:
                raise Exception(f"Erro Semântico [Linha {no.linha}]: Incompatibilidade de tipos. Tentou atribuir '{tipo_dir}' a uma variável do tipo '{tipo_esq}' ({no.variavel}).")

    def visitar_ChamadaFuncaoCmd(self, no):
        self.tabela.buscar(no.nome, no.linha)
        # Numa implementação avançada verificaríamos se os tipos e quantidade de parâmetros correspondem,
        # mas no momento só avaliamos se os argumentos não contêm erros semânticos internos.
        self.visitar(no.argumentos)

    def visitar_Retorne(self, no):
        if no.expressao:
            self.visitar(no.expressao)

    def visitar_BinOp(self, no):
        tipo_esq = self.visitar(no.esquerda)
        tipo_dir = self.visitar(no.direita)
        linha = no.linha
        op = no.operador
        
        # Operadores Relacionais e Lógicos resultam num valor booleano, que na nossa gramática pode ser tratado como INTEIRO
        if op in ['==', '!=', '>', '<', '>=', '<=', 'E', 'OU']:
            return 'INTEIRO'
            
        # Regras de Matemática
        if tipo_esq == 'INTEIRO' and tipo_dir == 'INTEIRO':
            return 'INTEIRO'
        elif tipo_esq == 'REAL' or tipo_dir == 'REAL':
            if tipo_esq in ['INTEIRO', 'REAL'] and tipo_dir in ['INTEIRO', 'REAL']:
                return 'REAL'
        
        raise Exception(f"Erro Semântico [Linha {linha}]: Operação '{op}' inválida entre '{tipo_esq}' e '{tipo_dir}'.")

    def visitar_UnOp(self, no):
        return self.visitar(no.operando)

    def visitar_Numero(self, no):
        if '.' in no.valor:
            return 'REAL'
        return 'INTEIRO'

    def visitar_Id(self, no):
        return self.tabela.buscar(no.nome, no.linha)

    def visitar_ChamadaFuncaoExpr(self, no):
        tipo_retorno = self.tabela.buscar(no.nome, no.linha)
        self.visitar(no.argumentos)
        return tipo_retorno
