from ast_nodes import *

class GeradorCodigo:
    def __init__(self):
        # Uma pilha de escopos (dicionários). O índice 0 é o escopo global.
        self.escopos_offsets = [{}]
        # As variáveis locais começam tipicamente do offset 2 para cima 
        # (se o offset 0 for RV e 1 for FBR antigo).
        self.proximo_offset_local = 2 
        self.contador_labels = 0

    def entrar_escopo(self):
        self.escopos_offsets.append({})
        # Ao entrar numa nova função, reiniciamos o contador de offsets locais
        self.proximo_offset_local = 2

    def sair_escopo(self):
        if len(self.escopos_offsets) > 1:
            self.escopos_offsets.pop()

    def nova_label(self, prefixo="LABEL"):
        self.contador_labels += 1
        return f"{prefixo}_{self.contador_labels}"

    def obter_offset(self, nome):
        # Procura da tabela mais interna (local) para a mais externa (global)
        for escopo in reversed(self.escopos_offsets):
            if nome in escopo:
                return escopo[nome]
        
        # BLOQUEIO RIGOROSO DAS VARIÁVEIS FANTASMA
        raise Exception(f"Erro no Gerador: Variável '{nome}' tentou ser usada sem ser alocada na memória!")

    def gerar(self, no_raiz):
        codigo = "// --- INÍCIO DO CÓDIGO SAM ---\n"
        
        # 1. Pula para a função principal
        codigo += "ADDSP 1 // Espaco para o RV da funcao principal\n"
        codigo += "JSR FUNCAO_principal\n"
        codigo += "STOP\n\n"
        
        # 2. Gera o código de todas as funções
        codigo += self.visitar(no_raiz)
        return codigo

    def visitar(self, no):
        if no is None: return ""
        
        # Se for uma lista, processa sequencialmente
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

    # ==========================================
    # Regras de Visita (Tradução para Assembly SaM)
    # ==========================================

    def visitar_Programa(self, no):
        # Em versão simplificada linear, percorremos todas as funções
        return self.visitar(no.funcoes)

    def visitar_Funcao(self, no):
        codigo = f"FUNCAO_{no.nome}:\n"
        
        self.entrar_escopo()
        
        # O número de argumentos desta função (importante para saber a posição do RV no Retorne)
        self.funcao_atual_num_args = len(no.parametros)
        
        # 1. Matemática de Offsets para Parâmetros:
        # Começando de -2 (pois o -1 será o Endereço de Retorno guardado pelo JSR)
        offset_parametro = -2
        for parametro in reversed(no.parametros):
            self.escopos_offsets[-1][parametro.nome] = offset_parametro
            offset_parametro -= 1
            
        # 2. Salva o FBR antigo e atualiza o FBR atual para o topo da pilha
        codigo += "LINK\n"
            
        # 3. Visita o bloco da função (variáveis locais começarão em +2)
        codigo += self.visitar(no.bloco)
        
        # 4. Encerra a função caso não haja return explícito
        codigo += "UNLINK\n"
        codigo += "RET\n\n"
        
        self.sair_escopo()
        return codigo

    def visitar_Bloco(self, no):
        codigo = self.visitar(no.declaracoes)
        codigo += self.visitar(no.comandos)
        return codigo

    def visitar_Declaracao(self, no):
        nome_var = no.nome
        # Criação LIMITADA APENAS À DECLARAÇÃO
        offset = self.proximo_offset_local
        self.escopos_offsets[-1][nome_var] = offset
        self.proximo_offset_local += 1
        
        # ADDSP 1 aloca o espaço no topo da pilha para guardar esta variável
        return f"ADDSP 1 // Aloca espaco para a variavel local '{nome_var}' (offset {offset})\n"

    def visitar_Id(self, no):
        # Se a variável não estiver no escopo, disparará erro fatal no obter_offset
        offset = self.obter_offset(no.nome)
        return f"PUSHOFF {offset} // Ler variavel '{no.nome}'\n"

    def visitar_Numero(self, no):
        return f"PUSHIMM {no.valor}\n"

    def visitar_Atribuicao(self, no):
        codigo = self.visitar(no.expressao)
        offset = self.obter_offset(no.variavel)
        codigo += f"STOREOFF {offset} // Guarda valor na variavel '{no.variavel}'\n"
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
            codigo += "// --- INICIO SENAO ---\n"
            codigo += self.visitar(no.senao_cmd)
            
        codigo += f"JUMP {label_fim}\n"
        
        codigo += f"{label_verdadeiro}:\n"
        codigo += "// --- INICIO ENTAO ---\n"
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
        codigo += f"STOREOFF {offset} // Inicializa iterador do 'para'\n"
        
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
        codigo += f"STOREOFF {offset} // Incrementa iterador\n"
        
        codigo += f"JUMP {label_inicio}\n"
        codigo += f"{label_fim}:\n"
        return codigo

    def visitar_ChamadaFuncaoCmd(self, no):
        codigo = f"// --- CHAMADA FUNCAO {no.nome} (CMD) ---\n"
        codigo += "ADDSP 1 // RV\n"
        for arg in no.argumentos:
            codigo += self.visitar(arg)
        codigo += f"JSR FUNCAO_{no.nome}\n"
        
        # Limpa argumentos
        num_args = len(no.argumentos)
        if num_args > 0:
            codigo += f"ADDSP -{num_args} // Limpa argumentos\n"
            
        # Limpa RV (já que é um comando e o valor não será usado)
        codigo += "ADDSP -1 // Limpa RV ignorado\n"
        return codigo

    def visitar_ChamadaFuncaoExpr(self, no):
        codigo = f"// --- CHAMADA FUNCAO {no.nome} (EXPR) ---\n"
        codigo += "ADDSP 1 // RV\n"
        for arg in no.argumentos:
            codigo += self.visitar(arg)
        codigo += f"JSR FUNCAO_{no.nome}\n"
        
        # Limpa argumentos (o topo da pilha passará a ser exatamente o RV!)
        num_args = len(no.argumentos)
        if num_args > 0:
            codigo += f"ADDSP -{num_args} // Limpa argumentos (RV fica no topo)\n"
        return codigo

    def visitar_Retorne(self, no):
        codigo = "// --- RETORNO ---\n"
        if no.expressao:
            codigo += self.visitar(no.expressao)
            
            # O RV fica abaixo de todos os N argumentos e do Endereço de Retorno (RA)
            # Posição = -(Num_Args + 2)
            offset_rv = -(self.funcao_atual_num_args + 2)
            codigo += f"STOREOFF {offset_rv} // Salva valor de retorno\n"
            
        codigo += "UNLINK\n"
        codigo += "RET\n"
        return codigo
