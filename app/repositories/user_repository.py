import sqlite3
from app.database.connection import get_connection
from app.models.user import User

# Responsável pelas operações de persistência dos usuários.
class UserRepository:

    # Inicializa o repositório com uma conexão ao banco de dados.
    def __init__(self, connection = None):
        self.connection = (
            connection if connection is not None
            else get_connection()
        )


    # Fecha a conexão com o banco.
    def close_connection(self):        
        if self.connection is not None:
            self.connection.close()
            self.connection = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()


    @staticmethod
    # Converte uma linha do banco de dados em um objeto User.
    def _row_to_user(row):

        if row is None:
            return None

        return User(
            id=row["id"],
            nome_completo=row["nome_completo"],
            email=row["email"],
            cpf=row["cpf"],
            senha=row["senha"],
            tipo_usuario_id=row["tipo_usuario_id"],
            status=row["status"],
            data_criacao=row["data_criacao"],
            data_atualizacao=row["data_atualizacao"],
            precisa_trocar_senha=bool(row["precisa_trocar_senha"]),
            solicitacao_reativacao=bool(row["solicitacao_reativacao"])
        )


    # Cria um novo usuário no banco de dados.
    def create_user(self, user: User):
        try:
            cursor = self.connection.execute("""
                INSERT INTO usuarios (
                    nome_completo, email, cpf, senha, tipo_usuario_id,
                    status, precisa_trocar_senha, solicitacao_reativacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.nome_completo,
                user.email,
                user.cpf,
                user.senha,
                user.tipo_usuario_id,
                user.status,
                user.precisa_trocar_senha,
                user.solicitacao_reativacao
            ))
            
            id = cursor.lastrowid
            self.connection.commit()

            return self.get_user_by_id(id)
        
        except sqlite3.Error:
            self.connection.rollback()
            raise


    # Consulta um usuário pelo ID no banco de dados.
    def get_user_by_id(self, user_id: int):
        try:
            cursor = self.connection.execute("""SELECT *
                                                  FROM usuarios
                                                 WHERE id = ?""", (user_id,)).fetchone()

            if cursor:
                return self._row_to_user(cursor)
            else:
                # raise ValueError("Usuário não encontrado")
                return None
        except sqlite3.Error:
            raise

    
    # Consulta o tipo de usuário pelo ID
    def get_user_type_by_id(self, tipo_usuario_id: int):
        cursor = self.connection.execute("""SELECT id, 
                                                   descricao 
                                              FROM tipos_usuario
                                             WHERE id = ?""",(tipo_usuario_id,)).fetchone()
        return cursor


    # Consulta um usuário pelo email no banco de dados.
    def get_user_by_email(self, email: str):
        try:
            cursor = self.connection.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
            
            if cursor:
                return self._row_to_user(cursor)

            return None
        
        except sqlite3.Error:
            raise


    # Consulta um usuário pelo CPF no banco de dados.
    def get_user_by_cpf(self, cpf: str):
        try:
            cursor = self.connection.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,)).fetchone()
            
            if cursor:
                return self._row_to_user(cursor)

            return None
        
        except sqlite3.Error:
            raise


    # Consul o tipo usuário pela descrição 
    def get_user_type_by_description(self, description: str):

        try:
            cursor = self.connection.execute(
                """
                SELECT id, descricao
                  FROM tipos_usuario
                 WHERE descricao = ?
                """,
                (description,)
            ).fetchone()

            return cursor

        except sqlite3.Error:
            raise
    

    # Lista todos os usuários no banco de dados.
    def get_all_users(self, include_excluded=True):
        
        if include_excluded:
            rows = self.connection.execute("""
                SELECT *
                  FROM usuarios
                 ORDER BY id
                """).fetchall()
        else:
            rows = self.connection.execute("""
                SELECT *
                  FROM usuarios
                 WHERE status != 'EXCLUIDO'
                 ORDER BY id
                """).fetchall()

        return [self._row_to_user(row) for row in rows]


    # Atualiza os dados de um usuário existente no banco de dados.
    def update_user(self, user: User):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                   SET nome_completo = ?,
                       email = ?, 
                       cpf = ?, 
                       senha = ?,
                       tipo_usuario_id = ?, 
                       status = ?, 
                       data_atualizacao = CURRENT_TIMESTAMP,
                       precisa_trocar_senha = ?, 
                       solicitacao_reativacao = ?
                 WHERE id = ?
            """, (
                user.nome_completo,
                user.email,
                user.cpf,
                user.senha,
                user.tipo_usuario_id,
                user.status,
                user.precisa_trocar_senha,
                user.solicitacao_reativacao,
                user.id
            ))

            if cursor.rowcount == 0:
                return None

            self.connection.commit()
            return self.get_user_by_id(user.id)
        
        except sqlite3.Error:
            self.connection.rollback()
            raise
        

    # Atualiza o status de um usuário no banco de dados.
    def update_user_status(self, user_id: int, new_status: str):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                SET status = ?, 
                data_atualizacao = CURRENT_TIMESTAMP,
                solicitacao_reativacao =
                       CASE
                           WHEN ? = 'ATIVO' THEN 0
                           ELSE solicitacao_reativacao
                       END
                WHERE id = ?
            """, (new_status, new_status, user_id))

            if cursor.rowcount == 0:
                return None

            self.connection.commit()
            return self.get_user_by_id(user_id)
        
        except sqlite3.Error:
            self.connection.rollback()
            raise
        

    # Atualiza a senha armazenada de um usuário no banco de dados.
    def update_user_password(self, user_id: int, new_password: str, precisa_trocar_senha: bool = False):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                   SET senha = ?, 
                       precisa_trocar_senha = ?, 
                       data_atualizacao = CURRENT_TIMESTAMP
                 WHERE id = ?
            """, (new_password, int(precisa_trocar_senha), user_id))

            if cursor.rowcount == 0:
                return None

            self.connection.commit()
            return self.get_user_by_id(user_id)
        
        except sqlite3.Error:
            self.connection.rollback()
            raise
        

    # Registra uma solicitação de reativação para um usuário no banco de dados.
    def request_reactivation(self, user_id: int):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                   SET solicitacao_reativacao = 1, 
                       data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND status = 'INATIVO'
                  AND solicitacao_reativacao = 0
            """, (user_id,))

            if cursor.rowcount == 0:
                return None

            self.connection.commit()
            return self.get_user_by_id(user_id)
        
        except sqlite3.Error:
            self.connection.rollback()
            raise


    # Consulta os usuários que possuem solicitações de reativação pendentes.
    def get_pending_reactivation_requests(self):

        rows = self.connection.execute("""
            SELECT *
              FROM usuarios
             WHERE status = 'INATIVO'
               AND solicitacao_reativacao = 1
             ORDER BY data_atualizacao ASC;
        """).fetchall()

        return [
            self._row_to_user(row)
            for row in rows
        ]


    # Aprova ou rejeita uma solicitação de reativação.
    def resolve_reactivation_request(self, user_id: int, approved: bool):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                   SET status = CASE
                       WHEN ? = 1 THEN 'ATIVO'
                       ELSE 'INATIVO'
                   END,
                       solicitacao_reativacao = 0,
                       data_atualizacao = CURRENT_TIMESTAMP
                 WHERE id = ?
                   AND status = 'INATIVO'
                   AND solicitacao_reativacao = 1;
            """, (int(approved), user_id))

            if cursor.rowcount == 0:
                self.connection.rollback()
                return None

            self.connection.commit()

            return self.get_user_by_id(user_id)

        except sqlite3.Error:
            self.connection.rollback()
            raise
    
        
    # Realiza a exclusão lógica de um usuário no banco de dados, alterando seu status para "EXCLUIDO".
    def delete_user(self, user_id: int):
        try:
            cursor = self.connection.execute("""
                UPDATE usuarios
                   SET status = 'EXCLUIDO',
                       solicitacao_reativacao = 0,
                       data_atualizacao = CURRENT_TIMESTAMP
                 WHERE id = ?
                   AND status != 'EXCLUIDO'
            """, (user_id,))

            if cursor.rowcount == 0:
                return None

            self.connection.commit()

            return self.get_user_by_id(user_id)

        except sqlite3.Error:
            self.connection.rollback()
            raise