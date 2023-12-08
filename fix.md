## Correções necessárias

1. a declaração de métodos não prevê o tipo dos parâmetros. Exemplo:

methods{
    int teste2(a){
        return 0;
    }
}

Deveria ser assim:

methods{
    int teste2(int a){
        return 0;
    }
}

No construtor também é necessário o tipo dos parâmetros!

---

2. No construtor é possível não atribuir nada à um atributo. Qual o sentido disso? Exemplo:

    constructor (a) {
        this.a;
    }

---

3.  Uma atribuição dentro de um método deve ser possível usar a palavra this. Exemplo.

    methods {

        int teste2(a){
            valor = this.a;
        }

    }

---

4. A variável de controle do for pode NÃO ser inicializada! É possível ter mais de uma variável de controle. Variável de controle pode ser inicializada com valores diferentes de inteiro. Outra coisa, como a linguagem tem um bloco variables para declaração de variáveis, não é necessário colocar o tipo da variável de controle.

    for(int a; i < MAX; i--) {
        print(i);
    }

    for(int a=10, b=20, c=a; i < MAX; i--) {
        print(i);
    }

    for(int a="teste for"; i < MAX; i--) {
        print(i);
    }

    for(int a = [1, 2, 3]; i < MAX; i--) {
        print(i);
    }

---

<!-- Resolvido -->

5. Problemas na atribuição

[X] - Não é possível atribuir o valor de um vetor ou matriz. Exemplo: a = vetor[i]; a = matriz[i][j];

[X] - Não é possível atribuir o valor de um atributo de objeto. Exemplo: a = objeto.valor;

---

6. Problemas na chamada de métodos

Não é possível atribuir o valor de retorno de um método. Exemplo: a = objeto->calcula(a,b);

Não é possível chamar um método void. Exemplo: obj.imprime(msg);

---

7. Expressões aritméticas

Não é possível atribuir o valor de uma simples expressão. Exemplo: a = 5 + 10 \* 2;

---

8. Expressões relacionais

Não é possível escrever:

if ( (valor > a && valor < b) || (valor >= c && valor < d) ) then { }

---

9. Recursão à esquerda

<Logical-Or-Expression> ::= <Logical-Not-Expression>
| <Logical-Or-Expression> '||' <Logical-Not-Expression>
| '(' <Logical-Or-Expression> ')'

<Logical-And-Expression> ::= <Logical-Or-Expression>
| <Logical-And-Expression> '&&' <Logical-Or-Expression>
| '(' <Logical-And-Expression> ')'

---

10. Fatoração à esquerda

<Method-Call> ::= IDE '(' <Args-List> ')'
<Primary-Expression> ::= IDE | NUM | BOOL | STR | <Method-Call>

<Expression> ::= <Declaration-Expression> | <Assignment-Expression>
<Declaration-Expression> ::= TYPE <IDE-List>
<Assignment-Expression> ::= TYPE IDE '=' <Logical-And-Expression> | IDE '=' <Logical-And-Expression>
