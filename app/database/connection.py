
import sqlite3
import hashlib
import hmac
import os

from pathlib import Path


# Localização da raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Diretório e arquivo do banco de dados
DATABASE_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATABASE_DIR / "userflow.db"


# Gerencia a conexão com o banco de dados
def get_connection():

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# Gera um hash seguro para a senha utilizando PBKDF2
def hash_password(password: str) -> str:

    salt = os.urandom(16)
    iterations = 600_000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )

    return (
        f"pbkdf2_sha256${iterations}$"
        f"{salt.hex()}${password_hash.hex()}"
    )


# Verifica se a senha corresponde ao hash armazenado
def verify_password(password: str, stored_hash: str) -> bool:

    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        if iterations <= 0:
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            iterations
        )

        return hmac.compare_digest(
            calculated_hash.hex(),
            expected_hash
        )

    except (ValueError, TypeError, AttributeError):
        return False


# Cria as tabelas do banco de dados
def _create_tables(connection):

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tipos_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT UNIQUE NOT NULL
        );
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo_usuario_id INTEGER NOT NULL,

            status TEXT NOT NULL DEFAULT 'ATIVO'
                CHECK (status IN ('ATIVO', 'INATIVO', 'EXCLUIDO')),

            data_criacao TEXT NOT NULL
                DEFAULT (
                    strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
                ),

            data_atualizacao TEXT,

            precisa_trocar_senha INTEGER NOT NULL DEFAULT 0
                CHECK (precisa_trocar_senha IN (0, 1)),

            solicitacao_reativacao INTEGER NOT NULL DEFAULT 0
                CHECK (solicitacao_reativacao IN (0, 1)),

            FOREIGN KEY (tipo_usuario_id)
                REFERENCES tipos_usuario(id)
        );
    """)


# Insere os tipos de usuários iniciais
def _seed_user_types(connection):

    connection.execute("""
        INSERT OR IGNORE INTO tipos_usuario (descricao)
        VALUES
            ('ADMIN'),
            ('USER');
    """)


# Configura a próxima matrícula para iniciar em 1000
def _set_initial_user_sequence(connection):

    max_id = connection.execute("""
        SELECT COALESCE(MAX(id), 0) AS max_id
        FROM usuarios;
    """).fetchone()["max_id"]

    initial_sequence = max(999, max_id)

    cursor = connection.execute("""
        UPDATE sqlite_sequence
        SET seq = ?
        WHERE name = 'usuarios';
    """, (initial_sequence,))

    if cursor.rowcount == 0:
        connection.execute("""
            INSERT INTO sqlite_sequence (name, seq)
            VALUES ('usuarios', ?);
        """, (initial_sequence,))


# Realiza a carga inicial dos usuários
def _seed_initial_users(connection):

    # Obtém os IDs dos tipos de usuários
    tipos = connection.execute("""
        SELECT id, descricao
        FROM tipos_usuario;
    """).fetchall()

    tipos_usuario = {
        tipo["descricao"]: tipo["id"]
        for tipo in tipos
    }

    # Dados fictícios para ambiente de desenvolvimento
    initial_users = [

        {
            "nome": "Administrador Principal",
            "email": "admin@teste.com",
            "cpf": "111.222.333-96",
            "senha": "teste123",
            "tipo": "ADMIN",
            "precisa_trocar_senha": False
        },

        {
            "nome": "Administrador Secundário",
            "email": "admin2@teste.com",
            "cpf": "222.333.444-05",
            "senha": "teste123",
            "tipo": "ADMIN",
            "precisa_trocar_senha": False
        },

        {
            "nome": "Usuario Teste 01",
            "email": "usuario01@teste.com",
            "cpf": "333.444.555-08",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": True
        },

        {
            "nome": "Usuario Teste 02",
            "email": "usuario02@teste.com",
            "cpf": "444.555.666-19",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": False
        },

        {
            "nome": "Usuario Teste 03",
            "email": "usuario03@teste.com",
            "cpf": "555.666.777-20",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": False,
            "status": "EXCLUIDO"
        },

        {
            "nome": "Usuario Teste 04",
            "email": "usuario04@teste.com",
            "cpf": "123.456.789-09",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": False,
            "status": "INATIVO"
        },

        {
            "nome": "Usuario Teste 05",
            "email": "usuario05@teste.com",
            "cpf": "987.654.321-00",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": False,
            "status": "INATIVO"
        },

        {
            "nome": "Usuario Teste 05",
            "email": "usuario05@teste.com",
            "cpf": "234.567.890-92",
            "senha": "teste123",
            "tipo": "USER",
            "precisa_trocar_senha": False,
            "status": "INATIVO"
        }
        
    ]

    for user in initial_users:

        # Verifica se o e-mail ou CPF já está cadastrado
        existing_user = connection.execute("""
            SELECT id
            FROM usuarios
            WHERE email = ? OR cpf = ?;
        """, (
            user["email"],
            user["cpf"]
        )).fetchone()

        if existing_user:
            continue

        connection.execute("""
            INSERT INTO usuarios (
                nome_completo,
                email,
                cpf,
                senha,
                tipo_usuario_id,
                status,
                precisa_trocar_senha
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            user["nome"],
            user["email"],
            user["cpf"],
            hash_password(user["senha"]),
            tipos_usuario[user["tipo"]],
            user.get("status", "ATIVO"),
            user["precisa_trocar_senha"]
        ))


# Inicializa o banco de dados
def initialize_database():

    connection = get_connection()

    try:

        _create_tables(connection)

        _seed_user_types(connection)

        _set_initial_user_sequence(connection)

        _seed_initial_users(connection)

        connection.commit()

        print("Banco de dados inicializado com sucesso!")

    except sqlite3.Error as error:

        connection.rollback()

        print(f"Erro ao inicializar o banco de dados: {error}")

        raise

    finally:

        connection.close()
