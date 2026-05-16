import re

PALAVRAS_RESERVADAS = {
    'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'print': 'PRINT',
    'true': 'TRUE', 'false': 'FALSE', 'def': 'DEF', 'return': 'RETURN'
}

TOKEN_SPEC = [
    # --- NOVAS REGRAS DE COMENTÁRIOS NO TOPO ---
    ('COMMENT_ML', r'/\*[\s\S]*?\*/'), # /* Qualquer coisa aqui dentro */
    ('COMMENT_SL', r'//.*'),           # // Qualquer coisa até ao fim da linha
    
    ('NUM',      r'\d+(\.\d+)?'),
    ('STRING',   r'"[^"]*"'),      
    ('BITOP',    r'<<|>>|&|\||\^'), 
    ('RELOP',    r'==|!=|<=|>=|<|>'), 
    ('ASSIGN',   r'='),            
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'), 
    ('OP',       r'[+\-*/]'),      
    ('LPAREN',   r'\('),           
    ('RPAREN',   r'\)'),           
    ('LBRACE',   r'\{'),           
    ('RBRACE',   r'\}'),  
    ('COMMA',    r','),            
    ('SEMI',     r';'),            
    ('SKIP',     r'[ \t\n]+'),     
    ('MISMATCH', r'.'),            
]

def analisar_lexico(codigo_fonte):
    tokens = []
    tok_regex = '|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in TOKEN_SPEC)
    linha_atual = 1
    
    for match in re.finditer(tok_regex, codigo_fonte):
        tipo_token = match.lastgroup
        valor = match.group()
        
        # --- ATUALIZAÇÃO NO TRATAMENTO DO TEXTO LIDO ---
        if tipo_token == 'SKIP':
            linha_atual += valor.count('\n')
            continue
        elif tipo_token in ('COMMENT_ML', 'COMMENT_SL'):
            # Ignoramos o comentário, mas contamos as quebras de linha
            # para que as mensagens de erro (se houverem) continuem na linha certa!
            linha_atual += valor.count('\n')
            continue
        elif tipo_token == 'MISMATCH':
            raise RuntimeError(f'Erro Léxico na linha {linha_atual}: Caractere inesperado "{valor}"')
        
        if tipo_token == 'ID' and valor in PALAVRAS_RESERVADAS:
            tipo_token = PALAVRAS_RESERVADAS[valor]
            
        tokens.append((tipo_token, valor, linha_atual))
        
    return tokens