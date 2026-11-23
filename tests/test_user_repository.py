
import sqlite3
import unittest

from app.models.user import User
from app.repositories.user_repository import UserRepository


class TestUserRepository(unittest.TestCase):

    def setUp(self):
        """Prepara um banco isolado para cada teste."""

        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.connection.executescript("""
            CREATE TABLE tipos_usuario (
                id INTEGER PRIMARY KEY,
                descricao TEXT NOT NULL UNIQUE
            );

            INSERT INTO tipos_usuario (id, descricao)
            VALUES (1, 'ADMIN'), (2, 'USUARIO');

            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                cpf TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo_usuario_id INTEGER NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('ATIVO', 'INATIVO', 'EXCLUIDO')),
                data_criacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TEXT,
                precisa_trocar_senha INTEGER NOT NULL DEFAULT 0,
                solicitacao_reativacao INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (tipo_usuario_id)
                    REFERENCES tipos_usuario(id)
            );
        """)

        self.repository = UserRepository(self.connection)


    def tearDown(self):
        """Fecha a conexão ao terminar cada teste."""

        self.repository.close_connection()


    def criar_usuario(
        self,
        nome="Usuário Teste",
        email="teste@example.com",
        cpf="12345678901",
        status="ATIVO"
    ):
        user = User(
            id=None,
            nome_completo=nome,
            email=email,
            cpf=cpf,
            senha="hash_teste",
            tipo_usuario_id=2,
            status=status
        )

        return self.repository.create_user(user)


    # 1. Cadastro de usuário
    def test_criar_usuario(self):

        user = self.criar_usuario()

        self.assertIsNotNone(user)
        self.assertEqual(user.nome_completo, "Usuário Teste")
        self.assertEqual(user.email, "teste@example.com")
        self.assertEqual(user.status, "ATIVO")
        self.assertGreaterEqual(user.id, 1)


    # 2. Consultar por matrícula
    def test_consultar_usuario_por_id(self):

        created = self.criar_usuario()

        user = self.repository.get_user_by_id(
            created.id
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.id, created.id)


    # 3. Consultar por e-mail
    def test_consultar_usuario_por_email(self):

        self.criar_usuario()

        user = self.repository.get_user_by_email(
            "teste@example.com"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "teste@example.com")


    # 4. Consultar por CPF
    def test_consultar_usuario_por_cpf(self):

        self.criar_usuario()

        user = self.repository.get_user_by_cpf(
            "12345678901"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.cpf, "12345678901")


    # 5. Usuário inexistente
    def test_usuario_nao_encontrado(self):

        user = self.repository.get_user_by_id(9999)

        self.assertIsNone(user)


    # 6. Impedir e-mail duplicado
    def test_impedir_email_duplicado(self):

        self.criar_usuario()

        with self.assertRaises(sqlite3.IntegrityError):
            self.criar_usuario(
                cpf="98765432100"
            )


    # 7. Impedir CPF duplicado
    def test_impedir_cpf_duplicado(self):

        self.criar_usuario()

        with self.assertRaises(sqlite3.IntegrityError):
            self.criar_usuario(
                email="outro@example.com"
            )


    # 8. Listar usuários
    def test_listar_usuarios(self):

        self.criar_usuario()

        self.criar_usuario(
            nome="Segundo Usuário",
            email="segundo@example.com",
            cpf="98765432100"
        )

        users = self.repository.get_all_users()

        self.assertEqual(len(users), 2)

    # 9. Atualizar dados cadastrais
    def test_atualizar_usuario(self):

        user = self.criar_usuario()

        user.nome_completo = "Nome Atualizado"

        updated = self.repository.update_user(user)

        self.assertEqual(
            updated.nome_completo,
            "Nome Atualizado"
        )

        self.assertIsNotNone(updated.data_atualizacao)


    # 10. Atualizar status
    def test_atualizar_status(self):

        user = self.criar_usuario()

        updated = self.repository.update_user_status(
            user.id,
            "INATIVO"
        )

        self.assertEqual(updated.status, "INATIVO")


    # 11. Solicitar reativação de usuário inativo
    def test_solicitar_reativacao(self):

        user = self.criar_usuario(status="INATIVO")

        updated = self.repository.request_reactivation(
            user.id
        )

        self.assertTrue(updated.solicitacao_reativacao)


    # 12. Não permitir solicitação para usuário ativo
    def test_nao_solicitar_reativacao_usuario_ativo(self):

        user = self.criar_usuario(status="ATIVO")

        result = self.repository.request_reactivation(
            user.id
        )

        self.assertIsNone(result)


    # 13. Atualizar senha
    def test_atualizar_senha(self):

        user = self.criar_usuario()

        updated = self.repository.update_user_password(
            user.id,
            "novo_hash"
        )

        self.assertEqual(updated.senha, "novo_hash")
        self.assertFalse(updated.precisa_trocar_senha)


    # 14. Exclusão lógica
    def test_exclusao_logica(self):

        user = self.criar_usuario()

        deleted = self.repository.delete_user(
            user.id
        )

        self.assertEqual(deleted.status, "EXCLUIDO")

        # O registro continua armazenado no banco.
        found = self.repository.get_user_by_id(
            user.id
        )

        self.assertIsNotNone(found)


    # 15. Não listar usuários excluídos
    def test_listar_sem_excluidos(self):

        self.criar_usuario()

        excluded = self.criar_usuario(
            nome="Usuário Excluído",
            email="excluido@example.com",
            cpf="11122233344"
        )

        self.repository.delete_user(excluded.id)

        users = self.repository.get_all_users(
            include_excluded=False
        )

        self.assertEqual(len(users), 1)


    # 16. Conexão continua aberta entre operações
    def test_reutilizar_conexao(self):

        self.criar_usuario()

        user = self.repository.get_user_by_email(
            "teste@example.com"
        )

        self.assertIsNotNone(user)

        users = self.repository.get_all_users()

        self.assertEqual(len(users), 1)


    # 17. Consultar solicitações de reativação pendentes
    def test_consultar_solicitacoes_reativacao_pendentes(self):

        user = self.criar_usuario(
            email="inativo@example.com",
            cpf="98765432100",
            status="INATIVO"
        )

        self.repository.request_reactivation(user.id)

        requests = self.repository.get_pending_reactivation_requests()

        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].id, user.id)
        self.assertEqual(requests[0].status, "INATIVO")
        self.assertTrue(requests[0].solicitacao_reativacao)


    # 18. Consulta sem solicitações pendentes
    def test_consulta_sem_solicitacoes_reativacao(self):
    
        requests = self.repository.get_pending_reactivation_requests()
    
        self.assertEqual(requests, [])


    # 19. Aprovar solicitação de reativação
    def test_aprovar_solicitacao_reativacao(self):

        user = self.criar_usuario(
            email="inativo@example.com",
            cpf="98765432100",
            status="INATIVO"
        )

        self.repository.request_reactivation(user.id)

        updated = self.repository.resolve_reactivation_request(
            user.id,
            approved=True
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "ATIVO")
        self.assertFalse(updated.solicitacao_reativacao)
        self.assertIsNotNone(updated.data_atualizacao)


    # 20. Rejeitar solicitação de reativação
    def test_rejeitar_solicitacao_reativacao(self):

        user = self.criar_usuario(
            email="inativo@example.com",
            cpf="98765432100",
            status="INATIVO"
        )

        self.repository.request_reactivation(user.id)

        updated = self.repository.resolve_reactivation_request(
            user.id,
            approved=False
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "INATIVO")
        self.assertFalse(updated.solicitacao_reativacao)
        self.assertIsNotNone(updated.data_atualizacao)


    # 21. Resolver solicitação inexistente
    def test_resolver_solicitacao_inexistente(self):

        result = self.repository.resolve_reactivation_request(
            user_id=9999,
            approved=True
        )

        self.assertIsNone(result)


    # 22. Não permitir resolver solicitação ja encerrada
    def test_nao_resolver_solicitacao_ja_encerrada(self):

        user = self.criar_usuario(
            email="inativo@example.com",
            cpf="98765432100",
            status="INATIVO"
        )

        self.repository.request_reactivation(user.id)

        # Primeira resolução: aprovação.
        first_result = self.repository.resolve_reactivation_request(
            user.id,
            approved=True
        )

        self.assertIsNotNone(first_result)

        # Segunda tentativa: a solicitação já foi encerrada.
        second_result = self.repository.resolve_reactivation_request(
            user.id,
            approved=False
        )

        self.assertIsNone(second_result)

        # Confirma que o usuário continua ativo.
        current_user = self.repository.get_user_by_id(user.id)

        self.assertEqual(current_user.status, "ATIVO")
        self.assertFalse(current_user.solicitacao_reativacao)


    

if __name__ == "__main__":
    unittest.main()
