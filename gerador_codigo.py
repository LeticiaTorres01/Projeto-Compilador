from arvore_ast import Num, Var, OpBinaria, Atribuicao, Bloco, If, While, Texto, Print, FuncaoDecl

class GeradorCodigo:
    def __init__(self):
        self.variaveis_declaradas = set()
        self.parametros_atuais = set() # Ajuda a não misturar parâmetros com variáveis globais

    def gerar(self, arvore):
        codigo_corpo = ""
        codigo_funcoes = ""

        # Separa o que são Funções do que é código principal
        for no in arvore:
            if isinstance(no, FuncaoDecl):
                codigo_funcoes += self.visitar(no) + "\n\n"
            else:
                codigo_corpo += self.visitar(no) + "\n"

        # 1. Cabeçalho
        codigo_final = "#include <stdio.h>\n"
        codigo_final += "#include <stdbool.h>\n\n"

        # 2. Variáveis Globais (usadas no corpo principal)
        if self.variaveis_declaradas:
            vars_str = ", ".join(self.variaveis_declaradas)
            codigo_final += f"float {vars_str};\n\n"

        # 3. Funções definidas pelo utilizador
        codigo_final += codigo_funcoes

        # 4. Função Main
        codigo_final += "int main() {\n"
        for linha in codigo_corpo.split('\n'):
            if linha.strip():
                codigo_final += f"    {linha}\n"
        codigo_final += "\n    return 0;\n"
        codigo_final += "}\n"

        return codigo_final

    # --- ATUALIZAR O VISITAR_ATRIBUICAO ---
    def visitar_Atribuicao(self, no):
        nome_var = no.variavel.nome
        # Só regista como global se não for um parâmetro da função atual
        if nome_var not in self.parametros_atuais:
            self.variaveis_declaradas.add(nome_var)
        expressao = self.visitar(no.expressao)
        return f"{nome_var} = {expressao};"

    # --- NOVOS MÉTODOS NO FINAL DO FICHEIRO ---
    def visitar_FuncaoDecl(self, no):
        # Regista os parâmetros para não os declarar como variáveis globais
        self.parametros_atuais = set(no.parametros)
        
        # Em C: float nome(float p1, float p2)
        params_c = ", ".join([f"float {p}" for p in no.parametros])
        codigo = f"float {no.nome}({params_c}) "
        codigo += self.visitar(no.bloco)
        
        # Limpa os parâmetros ao sair da função
        self.parametros_atuais = set() 
        return codigo

    def visitar_Chamada(self, no):
        # Avalia os argumentos que estão a ser passados
        args_c = ", ".join([self.visitar(arg) for arg in no.argumentos])
        return f"{no.nome}({args_c})"

    def visitar_Return(self, no):
        expressao = self.visitar(no.expressao)
        return f"return {expressao};"

    def visitar(self, no):
        """Descobre qual é o nó e chama o gerador correto para ele."""
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.erro_generico)
        return metodo(no)

    def erro_generico(self, no):
        raise Exception(f"Gerador de código não definido para {type(no).__name__}")

    def visitar_Num(self, no):
        # Em C, números são escritos da mesma forma
        return str(no.valor)

    def visitar_Var(self, no):
        return no.nome

    def visitar_OpBinaria(self, no):
        esq = self.visitar(no.esquerda)
        dir = self.visitar(no.direita)
        
        # Se for um operador bit-a-bit, força a conversão para inteiro no C
        if no.operador in ('&', '|', '^', '<<', '>>'):
            return f"((int){esq} {no.operador} (int){dir})"
            
        # Para matemática normal ou relacionais, mantém como estava
        return f"({esq} {no.operador} {dir})"

    def visitar_Atribuicao(self, no):
        # Regista que a variável existe e cria o código "var = expressão;"
        nome_var = no.variavel.nome
        self.variaveis_declaradas.add(nome_var)
        expressao = self.visitar(no.expressao)
        return f"{nome_var} = {expressao};"

    def visitar_Bloco(self, no):
        # Abre chaves e coloca todas as instruções lá dentro
        codigo = "{\n"
        for instrucao in no.instrucoes:
            linha = self.visitar(instrucao)
            codigo += f"    {linha}\n"
        codigo += "}"
        return codigo

    def visitar_If(self, no):
        condicao = self.visitar(no.condicao)
        bloco_verdadeiro = self.visitar(no.bloco_verdadeiro)
        
        # Em C, a condição do if tem de ter parênteses à volta
        codigo = f"if ({condicao}) {bloco_verdadeiro}"
        
        if no.bloco_falso:
            bloco_falso = self.visitar(no.bloco_falso)
            codigo += f" else {bloco_falso}"
            
        return codigo

    def visitar_While(self, no):
        condicao = self.visitar(no.condicao)
        bloco = self.visitar(no.bloco)
        return f"while ({condicao}) {bloco}"
    
    def visitar_Texto(self, no):
        # A string já vem com as aspas do Scanner
        return no.valor

    def visitar_Print(self, no):
        expressao_gerada = self.visitar(no.expressao)
        
        # Em C, imprimir texto e imprimir números exige formatos diferentes.
        # Fazemos uma verificação simples: se o nó for Texto, usamos "%s"
        if isinstance(no.expressao, Texto):
            return f'printf("%s\\n", {expressao_gerada});'
        else:
            # Se for variável ou número, assumimos que é um float (%.2f para 2 casas decimais)
            return f'printf("%.2f\\n", {expressao_gerada});'
        
    def visitar_Booleano(self, no):
        # Transforma o True/False do Python no true/false do C
        return "true" if no.valor else "false"