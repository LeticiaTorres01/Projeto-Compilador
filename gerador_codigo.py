from ast_nodes import *

class GeradorCodigo:
    def __init__(self):
        self.escopos_offsets = [{}]
        self.proximo_offset_local = 2 
        self.contador_labels = 0

    def entrar_escopo(self):
        self.escopos_offsets.append({})
        self.proximo_offset_local = 2

    def sair_escopo(self):
        if len(self.escopos_offsets) > 1:
            self.escopos_offsets.pop()

    def nova_label(self, prefixo="LABEL"):
        self.contador_labels += 1
        return f"{prefixo}_{self.contador_labels}"

    def obter_offset(self, nome):
        for escopo in reversed(self.escopos_offsets):
            if nome in escopo:
                return escopo[nome]
        raise Exception(f"Erro no Gerador: Variável '{nome}' tentou ser usada sem ser alocada na memória!")

    def gerar(self, no_raiz):
        codigo = "ADDSP 1\n"
        codigo += "LINK\n"
        codigo += "JSR FUNCAO_principal\n"
        codigo += "POPFBR\n"
        codigo += "STOP\n"
        codigo += self.visitar(no_raiz)
        return codigo

    def visitar(self, no):
        if no is None: return ""
        if isinstance(no, list):
            codigo = ""
            for item in no:
                codigo += self.visitar(item)
            return codigo
        nome_metodo = f'visitar_{type(no).__name__}'
        visitante = getattr(self, nome_metodo, self.erro_generico)
        return visitante(no)

    def erro_generico(self, no):
        raise Exception(f"Geração de Código: Nenhum método visitar_{type(no).__name__} definido.")

    def visitar_Programa(self, no):
        return self.visitar(no.funcoes)

    def visitar_Funcao(self, no):
        codigo = f"FUNCAO_{no.nome}:\n"
        self.entrar_escopo()
        self.funcao_atual_num_args = len(no.parametros)
        self.funcao_atual_num_locais = 0
        
        offset_parametro = -1
        for parametro in reversed(no.parametros):
            self.escopos_offsets[-1][parametro.nome] = offset_parametro
            offset_parametro -= 1
            
        codigo += self.visitar(no.bloco)
        
        if not codigo.endswith("JUMPIND\n"):
            if self.funcao_atual_num_locais > 0:
                codigo += f"ADDSP -{self.funcao_atual_num_locais}\n"
            codigo += "JUMPIND\n"
        
        self.sair_escopo()
        return codigo

    def visitar_Bloco(self, no):
        codigo = self.visitar(no.declaracoes)
        codigo += self.visitar(no.comandos)
        return codigo

    def visitar_Declaracao(self, no):
        nome_var = no.nome
        offset = self.proximo_offset_local
        self.escopos_offsets[-1][nome_var] = offset
        self.proximo_offset_local += 1
        self.funcao_atual_num_locais += 1
        return f"ADDSP 1\n"

    def visitar_Id(self, no):
        offset = self.obter_offset(no.nome)
        return f"PUSHOFF {offset}\n"

    def visitar_Numero(self, no):
        return f"PUSHIMM {no.valor}\n"

    def visitar_Atribuicao(self, no):
        codigo = self.visitar(no.expressao)
        offset = self.obter_offset(no.variavel)
        codigo += f"STOREOFF {offset}\n"
        return codigo

    def visitar_BinOp(self, no):
        codigo = self.visitar(no.esquerda)
        codigo += self.visitar(no.direita)
        op = no.operador
        if op == '+': codigo += "ADD\n"
        elif op == '-': codigo += "SUB\n"
        elif op == '*': codigo += "TIMES\n"
        elif op == '/': codigo += "DIV\n"
        elif op == '%': codigo += "MOD\n"
        elif op == '>': codigo += "GREATER\n"
        elif op == '<': codigo += "LESS\n"
        elif op == '==': codigo += "EQUAL\n"
        elif op == '>=': codigo += "LESS\nNOT\n"
        elif op == '<=': codigo += "GREATER\nNOT\n"
        elif op == '!=': codigo += "EQUAL\nNOT\n"
        elif op == 'E': codigo += "AND\n"
        elif op == 'OU': codigo += "OR\n"
        return codigo

    def visitar_UnOp(self, no):
        codigo = self.visitar(no.operando)
        if no.operador == 'NAO':
            codigo += "NOT\n"
        return codigo

    def visitar_Se(self, no):
        label_verdadeiro = self.nova_label("VERDADEIRO")
        label_fim = self.nova_label("FIM_SE")
        codigo = self.visitar(no.condicao)
        codigo += f"JUMPC {label_verdadeiro}\n"
        if no.senao_cmd:
            codigo += self.visitar(no.senao_cmd)
        codigo += f"JUMP {label_fim}\n"
        codigo += f"{label_verdadeiro}:\n"
        codigo += self.visitar(no.entao_cmd)
        codigo += f"{label_fim}:\n"
        return codigo

    def visitar_Enquanto(self, no):
        label_inicio = self.nova_label("ENQUANTO_INICIO")
        label_fim = self.nova_label("ENQUANTO_FIM")
        codigo = f"{label_inicio}:\n"
        codigo += self.visitar(no.condicao)
        codigo += "NOT\n"
        codigo += f"JUMPC {label_fim}\n"
        codigo += self.visitar(no.comandos)
        codigo += f"JUMP {label_inicio}\n"
        codigo += f"{label_fim}:\n"
        return codigo

    def visitar_FacaEnquanto(self, no):
        label_inicio = self.nova_label("FACA_INICIO")
        codigo = f"{label_inicio}:\n"
        codigo += self.visitar(no.comandos)
        codigo += self.visitar(no.condicao)
        codigo += f"JUMPC {label_inicio}\n"
        return codigo

    def visitar_Para(self, no):
        offset = self.obter_offset(no.variavel)
        codigo = self.visitar(no.inicio)
        codigo += f"STOREOFF {offset}\n"
        label_inicio = self.nova_label("PARA_INICIO")
        label_fim = self.nova_label("PARA_FIM")
        codigo += f"{label_inicio}:\n"
        codigo += f"PUSHOFF {offset}\n"
        codigo += self.visitar(no.fim)
        codigo += "GREATER\n"
        codigo += f"JUMPC {label_fim}\n"
        codigo += self.visitar(no.comandos)
        codigo += f"PUSHOFF {offset}\n"
        codigo += "PUSHIMM 1\n"
        codigo += "ADD\n"
        codigo += f"STOREOFF {offset}\n"
        codigo += f"JUMP {label_inicio}\n"
        codigo += f"{label_fim}:\n"
        return codigo

    def visitar_ChamadaFuncaoCmd(self, no):
        codigo = "ADDSP 1\n"
        for arg in no.argumentos:
            codigo += self.visitar(arg)
        codigo += "LINK\n"
        codigo += f"JSR FUNCAO_{no.nome}\n"
        codigo += "POPFBR\n"
        num_args = len(no.argumentos)
        if num_args > 0:
            codigo += f"ADDSP -{num_args}\n"
        codigo += "ADDSP -1\n"
        return codigo

    def visitar_ChamadaFuncaoExpr(self, no):
        codigo = "ADDSP 1\n"
        for arg in no.argumentos:
            codigo += self.visitar(arg)
        codigo += "LINK\n"
        codigo += f"JSR FUNCAO_{no.nome}\n"
        codigo += "POPFBR\n"
        num_args = len(no.argumentos)
        if num_args > 0:
            codigo += f"ADDSP -{num_args}\n"
        return codigo

    def visitar_Retorne(self, no):
        codigo = ""
        if no.expressao:
            codigo += self.visitar(no.expressao)
            offset_rv = -(self.funcao_atual_num_args + 1)
            codigo += f"STOREOFF {offset_rv}\n"
        if self.funcao_atual_num_locais > 0:
            codigo += f"ADDSP -{self.funcao_atual_num_locais}\n"
        codigo += "JUMPIND\n"
        return codigo
