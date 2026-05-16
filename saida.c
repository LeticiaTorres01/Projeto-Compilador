#include <stdio.h>
#include <stdbool.h>

float nome, idade, usuario_ativo;

int main() {
    printf("%s\n", "Testando Semantica...");
    nome = "Leticia";
    idade = 22.0;
    usuario_ativo = true;
    if ((usuario_ativo == true)) {
        printf("%s\n", "Bem vindo!");
    }

    return 0;
}
