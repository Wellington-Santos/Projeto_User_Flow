# UserFlow --- Sistema de Gestão de Usuários

## 1. Sobre o projeto

O **UserFlow** é uma aplicação desktop desenvolvida em Python para
gerenciamento de usuários, com autenticação, controle de acesso por
perfil e administração de contas.

O projeto foi desenvolvido com foco em organização de código, separação
de responsabilidades, segurança no tratamento de senhas, persistência de
dados e aplicação de regras de negócio.

## 2. Funcionalidades

-   Autenticação de usuários por e-mail e senha.
-   Cadastro de usuários por administradores.
-   Controle de acesso por perfil: `ADMIN` e `USER`.
-   Edição de dados cadastrais conforme as permissões do usuário.
-   Validação de e-mail e CPF.
-   Armazenamento de senhas utilizando PBKDF2 com SHA-256 e salt
    individual.
-   Definição de senha temporária por administrador.
-   Obrigatoriedade de troca da senha no primeiro acesso, quando
    aplicável.
-   Alteração de senha pelo próprio usuário.
-   Consulta e gerenciamento de usuários.
-   Alteração de status: `ATIVO`, `INATIVO` e `EXCLUIDO`.
-   Exclusão lógica de usuários, preservando os registros no banco de
    dados.
-   Solicitação de reativação de contas inativas.
-   Aprovação ou rejeição de solicitações de reativação por
    administradores.
-   Testes automatizados das regras de negócio.

## 3. Tecnologias utilizadas

-   **Python:** linguagem de programação.
-   **SQLite:** banco de dados relacional.
-   **Tkinter:** desenvolvimento da interface gráfica.
-   **Unittest:** testes automatizados.
-   **PBKDF2 / SHA-256:** proteção das senhas.
-   **email-validator:** validação de endereços de e-mail.
-   **validate-docbr:** validação de CPF.

## 4. Arquitetura do projeto

A aplicação utiliza separação de responsabilidades entre as camadas:

-   **Models:** representação das entidades da aplicação.
-   **Repositories:** operações de persistência e consultas ao banco de
    dados.
-   **Services:** regras de negócio, validações e controle de
    permissões.
-   **Views:** interface gráfica e interação com o usuário.
-   **Tests:** testes automatizados dos serviços e regras de negócio.

## 5. Estrutura de diretórios

``` text
UserFlow/
│
├── app/
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   └── user.py
│   │
│   ├── repositories/
│   │   └── user_repository.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   └── validators.py
│   │
│   ├── utils/
│   │   └── window_utils.py
│   │
│   └── views/
│       ├── login_view.py
│       ├── dashboard_view.py
│       ├── change_password_view.py
│       ├── user_management_view.py
│       └── edit_user_view.py
│
├── data/
├── tests/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 6. Requisitos para execução

-   Python 3.10 ou superior.
-   Pip.
-   Instalação do Tkinter disponível na distribuição Python utilizada.

## 7. Instalação

Clone o repositório:

``` bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta do projeto:

``` bash
cd UserFlow
```

Crie um ambiente virtual:

``` bash
python -m venv venv
```

Ative o ambiente virtual no Windows:

``` bash
venv\\Scripts\\activate
```

Instale as dependências:

``` bash
pip install -r requirements.txt
```

## 8. Execução

Execute a aplicação pela raiz do projeto:

``` bash
python main.py
```

O banco de dados SQLite é inicializado pela aplicação por meio da rotina
de inicialização.

## 9. Testes automatizados

Para executar os testes:

``` bash
python -m unittest discover -s tests -v
```

## 10. Regras de negócio e segurança

O UserFlow implementa regras de controle de acesso para diferenciar as
operações disponíveis aos administradores e usuários comuns.

As senhas não são armazenadas em texto puro. A aplicação utiliza PBKDF2
com SHA-256, salt individual e número configurado de iterações.

A exclusão de usuários é lógica: o registro permanece armazenado, com
alteração de status para `EXCLUIDO`.

Usuários inativos não podem realizar autenticação, mas podem solicitar
reativação da conta. A decisão sobre a solicitação é realizada por um
administrador.

## 11. Objetivo técnico

O projeto demonstra a aplicação prática de conceitos de desenvolvimento
back-end e engenharia de software, incluindo:

-   Separação de responsabilidades.
-   Encapsulamento das regras de negócio.
-   Persistência com banco de dados relacional.
-   Validação e normalização de dados.
-   Controle de acesso.
-   Segurança de credenciais.
-   Tratamento de exceções.
-   Testes automatizados.

## 12. Melhorias futuras

-   Implementação de novos níveis de auditoria.
-   Evolução da interface gráfica.
-   Ampliação da cobertura de testes.
-   Disponibilização de uma API REST.
-   Migração para uma arquitetura cliente-servidor, caso necessário.
