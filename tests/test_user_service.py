
import unittest
import copy

from unittest.mock import Mock, patch
from app.models.user import User
from app.services.user_service import UserService


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.repository = Mock()
        self.service = UserService(repository=self.repository)

        # Simula um tipo de usuário existente.
        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        # Simula que não existem usuários com os dados informados.
        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_cpf.return_value = None

        # Simula o retorno do cadastro.
        self.usuario_criado = User(
            id=1000,
            nome_completo="João da Silva",
            email="joao@email.com",
            cpf="52998224725",
            senha="hash_da_senha",
            tipo_usuario_id=2,
            status="ATIVO"
        )

        self.usuario_inativo = User(
            id=1001,
            nome_completo="Maria da Silva",
            email="maria@email.com",
            cpf="11144477735",
            senha="hash_da_senha",
            tipo_usuario_id=2,
            status="INATIVO",
            solicitacao_reativacao=True
        )

        self.administrador = User(
            id=1002,
            nome_completo="Carlos Administrador",
            email="carlos@email.com",
            cpf="93541134780",
            senha="hash_da_senha",
            tipo_usuario_id=1,
            status="ATIVO"
        )

        self.usuario_excluido = copy.deepcopy(self.usuario_criado)
        self.usuario_excluido.status = "EXCLUIDO"

        self.repository.create_user.return_value = self.usuario_criado


    # 1. Teste para criar usuário com sucesso
    @patch("app.services.user_service.hash_password")
    def test_criar_usuario_com_sucesso(self, mock_hash):
        mock_hash.return_value = "hash_da_senha"

        usuario = self.service.create_user(
            nome_completo="João da Silva",
            email="JOAO@email.com",
            cpf="529.982.247-25",
            senha="Senha123",
            tipo_usuario_id=2
        )

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nome_completo, "João da Silva")
        self.assertEqual(usuario.email, "joao@email.com")
        self.assertEqual(usuario.cpf, "52998224725")
        self.assertEqual(usuario.status, "ATIVO")

        mock_hash.assert_called_once_with("Senha123")
        self.repository.create_user.assert_called_once()


    # 2. Teste para criar usuário com e-mail duplicado
    def test_nao_criar_usuario_com_email_duplicado(self):
        self.repository.get_user_by_email.return_value = self.usuario_criado

        with self.assertRaisesRegex(ValueError, "e-mail já está cadastrado"):
            self.service.create_user(
                "João da Silva",
                "joao@email.com",
                "529.982.247-25",
                "Senha123",
                2
            )

        self.repository.create_user.assert_not_called()


    # 3. Teste para criar usuário com CPF duplicado
    def test_nao_criar_usuario_com_cpf_duplicado(self):
        self.repository.get_user_by_cpf.return_value = self.usuario_criado

        with self.assertRaisesRegex(ValueError, "CPF já está cadastrado"):
            self.service.create_user(
                "João da Silva",
                "joao@email.com",
                "529.982.247-25",
                "Senha123",
                2
            )

        self.repository.create_user.assert_not_called()


    # 4. Teste para criar usuário com tipo de usuário inexistente
    def test_nao_criar_usuario_com_tipo_inexistente(self):
        self.repository.get_user_type_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Tipo de usuário não encontrado"):
            self.service.create_user(
                "João da Silva",
                "joao@email.com",
                "529.982.247-25",
                "Senha123",
                99
            )

        self.repository.create_user.assert_not_called()


    # 5. Teste para criar usuário com nome inválido (menos de 3 caracteres)
    def test_nao_criar_usuario_com_nome_invalido(self):
        with self.assertRaises(ValueError):
            self.service.create_user(
                "Jo",
                "joao@email.com",
                "529.982.247-25",
                "Senha123",
                2
            )

        self.repository.create_user.assert_not_called()


    # 6. Teste para criar usuário com e-mail inválido
    def test_nao_criar_usuario_com_email_invalido(self):
        with self.assertRaises(ValueError):
            self.service.create_user(
                "João da Silva",
                "email_invalido",
                "529.982.247-25",
                "Senha123",
                2
            )

        self.repository.create_user.assert_not_called()


    # 7. Teste para criar usuário com CPF inválido
    def test_nao_criar_usuario_com_cpf_invalido(self):
        with self.assertRaises(ValueError):
            self.service.create_user(
                "João da Silva",
                "joao@email.com",
                "111.111.111-11",
                "Senha123",
                2
            )

        self.repository.create_user.assert_not_called()


    # 8. Teste para criar usuário com senha curta (menos de 6 caracteres)
    def test_nao_criar_usuario_com_senha_curta(self):
        with self.assertRaises(ValueError):
            self.service.create_user(
                "João da Silva",
                "joao@email.com",
                "529.982.247-25",
                "1234",
                2
            )

        self.repository.create_user.assert_not_called()


    # 9. Consultar solicitações de reativação pendentes
    def test_consultar_solicitacoes_reativacao_pendentes(self):

        self.repository.get_pending_reactivation_requests.return_value = [
            self.usuario_inativo
        ]

        requests = self.service.get_pending_reactivation_requests()

        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].id, 1001)
        self.assertEqual(requests[0].status, "INATIVO")
        self.assertTrue(requests[0].solicitacao_reativacao)

        self.repository.get_pending_reactivation_requests.assert_called_once()


    # 10. Consultar quando não existem solicitações pendentes
    def test_consultar_sem_solicitacoes_reativacao(self):

        self.repository.get_pending_reactivation_requests.return_value = []

        requests = self.service.get_pending_reactivation_requests()

        self.assertEqual(requests, [])
        self.repository.get_pending_reactivation_requests.assert_called_once()


    # 11. Aprovar solicitação de reativação
    def test_aprovar_solicitacao_reativacao(self):

        usuario_inativo = copy.deepcopy(self.usuario_inativo)

        usuario_reativado = copy.deepcopy(usuario_inativo)
        usuario_reativado.status = "ATIVO"
        usuario_reativado.solicitacao_reativacao = False

        self.repository.get_user_by_id.return_value = usuario_inativo
        self.repository.resolve_reactivation_request.return_value = usuario_reativado

        result = self.service.approve_reactivation_request(1001)

        self.assertEqual(result.status, "ATIVO")
        self.assertFalse(result.solicitacao_reativacao)

        self.repository.resolve_reactivation_request.assert_called_once_with(
            1001,
            approved=True
        )



    # 12. Rejeitar solicitação de reativação
    def test_rejeitar_solicitacao_reativacao(self):

        import copy

        usuario_rejeitado = copy.deepcopy(self.usuario_inativo)
        usuario_rejeitado.solicitacao_reativacao = False

        self.repository.get_user_by_id.return_value = self.usuario_inativo
        self.repository.resolve_reactivation_request.return_value = usuario_rejeitado

        result = self.service.reject_reactivation_request(1001)

        self.assertEqual(result.status, "INATIVO")
        self.assertFalse(result.solicitacao_reativacao)

        self.repository.resolve_reactivation_request.assert_called_once_with(
            1001,
            approved=False
        )
    

    # 13. Teste com usuário inexistente
    def test_nao_aprovar_reativacao_usuario_inexistente(self):

        self.repository.get_user_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuário não encontrado"):
            self.service.approve_reactivation_request(9999)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 14. Teste não aprovar reativacao usuario ativo
    def test_nao_aprovar_reativacao_usuario_ativo(self):

        self.repository.get_user_by_id.return_value = self.usuario_criado

        with self.assertRaisesRegex(ValueError, "Somente usuários inativos"):
            self.service.approve_reactivation_request(1000)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 15. Teste Usuário sem solicitação pendente
    def test_nao_aprovar_usuario_sem_solicitacao_pendente(self):

        usuario_sem_solicitacao = copy.deepcopy(self.usuario_inativo)
        usuario_sem_solicitacao.solicitacao_reativacao = False

        self.repository.get_user_by_id.return_value = usuario_sem_solicitacao

        with self.assertRaisesRegex(ValueError, "solicitação de reativação pendente"):
            self.service.approve_reactivation_request(1001)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 16. Teste não rejeitar usuário inexistente
    def test_nao_rejeitar_reativacao_usuario_inexistente(self):

        self.repository.get_user_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuário não encontrado"):
            self.service.reject_reactivation_request(9999)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 17. Teste não rejeitar usuário ativo
    def test_nao_rejeitar_reativacao_usuario_ativo(self):

        self.repository.get_user_by_id.return_value = self.usuario_criado

        with self.assertRaisesRegex(ValueError, "Somente usuários inativos"):
            self.service.reject_reactivation_request(1000)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 18. Teste não rejeitar usuário sem solicitação
    def test_nao_rejeitar_usuario_sem_solicitacao_pendente(self):
 
        usuario_sem_solicitacao = copy.deepcopy(self.usuario_inativo)
        usuario_sem_solicitacao.solicitacao_reativacao = False

        self.repository.get_user_by_id.return_value = usuario_sem_solicitacao

        with self.assertRaisesRegex(ValueError, "solicitação de reativação pendente"):
            self.service.reject_reactivation_request(1001)

        self.repository.resolve_reactivation_request.assert_not_called()


    # 19. Administrador exclui usuário com sucesso
    def test_excluir_usuario_com_sucesso(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        usuario_excluido = copy.deepcopy(usuario)
        usuario_excluido.status = "EXCLUIDO"

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.delete_user.return_value = usuario_excluido

        result = self.service.delete_user(
            user_id=1000,
            requesting_user_id=1002
        )

        self.assertEqual(result.status, "EXCLUIDO")

        self.repository.delete_user.assert_called_once_with(1000)


    # 20. Administrador não pode excluir a própria conta
    def test_nao_excluir_propria_conta(self):

        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            administrador,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        with self.assertRaisesRegex(ValueError, "própria conta"):
            self.service.delete_user(
                user_id=1002,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_not_called()


    # 21. Usuário comum não pode excluir outro usuário
    def test_nao_excluir_usuario_sem_permissao_administrativa(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        with self.assertRaisesRegex(ValueError, "Apenas administradores"):
            self.service.delete_user(
                user_id=1000,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_not_called()


    # 22. Administrador inativo não pode excluir usuários
    def test_nao_excluir_usuario_com_administrador_inativo(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)
        administrador.status = "INATIVO"

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        with self.assertRaisesRegex(ValueError, "administradores ativos"):
            self.service.delete_user(
                user_id=1000,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_not_called()


    # 23. Não excluir usuário inexistente
    def test_nao_excluir_usuario_inexistente(self):

        self.repository.get_user_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuário não encontrado"):
            self.service.delete_user(
                user_id=9999,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_not_called()


    # 24. Não excluir usuário já excluído
    def test_nao_excluir_usuario_ja_excluido(self):

        usuario = copy.deepcopy(self.usuario_excluido)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        with self.assertRaisesRegex(ValueError, "já foi excluído"):
            self.service.delete_user(
                user_id=1000,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_not_called()


    # 25. Solicitante inexistente
    def test_nao_excluir_usuario_com_administrador_inexistente(self):

        usuario = copy.deepcopy(self.usuario_criado)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            None
        ]

        with self.assertRaisesRegex(
            ValueError,
            "Administrador solicitante não encontrado"
        ):
            self.service.delete_user(
                user_id=1000,
                requesting_user_id=9999
            )

        self.repository.delete_user.assert_not_called()


    # 26. Repository não consegue concluir a exclusão
    def test_excluir_usuario_com_falha_no_repository(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.delete_user.return_value = None

        with self.assertRaisesRegex(ValueError, "Não foi possível excluir"):
            self.service.delete_user(
                user_id=1000,
                requesting_user_id=1002
            )

        self.repository.delete_user.assert_called_once_with(1000)


        # 27. Consultar todos os usuários
    def test_consultar_todos_usuarios(self):

        usuarios = [
            copy.deepcopy(self.usuario_criado),
            copy.deepcopy(self.usuario_inativo),
            copy.deepcopy(self.usuario_excluido)
        ]

        self.repository.get_all_users.return_value = usuarios

        result = self.service.get_all_users()

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].status, "ATIVO")
        self.assertEqual(result[1].status, "INATIVO")
        self.assertEqual(result[2].status, "EXCLUIDO")

        self.repository.get_all_users.assert_called_once_with(
            include_excluded=True
        )


    # 28. Consultar usuários sem incluir os excluídos
    def test_consultar_usuarios_sem_excluidos(self):

        usuarios = [
            copy.deepcopy(self.usuario_criado),
            copy.deepcopy(self.usuario_inativo)
        ]

        self.repository.get_all_users.return_value = usuarios

        result = self.service.get_all_users(include_excluded=False)

        self.assertEqual(len(result), 2)

        for usuario in result:
            self.assertNotEqual(usuario.status, "EXCLUIDO")

        self.repository.get_all_users.assert_called_once_with(
            include_excluded=False
        )


    # 29. Administrador altera usuário de ATIVO para INATIVO
    def test_administrador_inativar_usuario_com_sucesso(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        usuario_inativado = copy.deepcopy(usuario)
        usuario_inativado.status = "INATIVO"

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.update_user_status.return_value = usuario_inativado

        result = self.service.update_user_status(
            user_id=1000,
            new_status="INATIVO",
            requesting_user_id=1002
        )

        self.assertEqual(result.status, "INATIVO")

        self.repository.update_user_status.assert_called_once_with(
            1000,
            "INATIVO"
        )


    # 30. Administrador reativa usuário INATIVO
    def test_administrador_reativar_usuario_com_sucesso(self):

        usuario = copy.deepcopy(self.usuario_inativo)
        administrador = copy.deepcopy(self.administrador)
    
        usuario_reativado = copy.deepcopy(usuario)
        usuario_reativado.status = "ATIVO"
        usuario_reativado.solicitacao_reativacao = False
    
        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]
    
        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }
    
        self.repository.update_user_status.return_value = usuario_reativado
    
        result = self.service.update_user_status(
            user_id=1001,
            new_status="ATIVO",
            requesting_user_id=1002
        )
    
        self.assertEqual(result.status, "ATIVO")
        self.assertFalse(result.solicitacao_reativacao)
    
        self.repository.update_user_status.assert_called_once_with(
            1001,
            "ATIVO"
        )

    # 31. Administrador não pode alterar o próprio status
    def test_nao_alterar_proprio_status(self):

        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            administrador,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        with self.assertRaisesRegex(ValueError, "próprio status"):
            self.service.update_user_status(
                user_id=1002,
                new_status="INATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()

    # 32. Usuário comum não pode alterar status
    def test_usuario_comum_nao_alterar_status(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        with self.assertRaisesRegex(ValueError, "Apenas administradores"):
            self.service.update_user_status(
                user_id=1000,
                new_status="INATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()

    # 33. Administrador inativo não pode alterar status
    def test_administrador_inativo_nao_alterar_status(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)
        administrador.status = "INATIVO"

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        with self.assertRaisesRegex(ValueError, "não está ativo"):
            self.service.update_user_status(
                user_id=1000,
                new_status="INATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()

    # 34. Não alterar usuário inexistente
    def test_nao_alterar_status_usuario_inexistente(self):

        self.repository.get_user_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuário não encontrado"):
            self.service.update_user_status(
                user_id=9999,
                new_status="INATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()

    # 35. Não permitir status inválido
    def test_nao_permitir_status_invalido(self):

        with self.assertRaisesRegex(ValueError, "Status informado não é permitido"):
            self.service.update_user_status(
                user_id=1000,
                new_status="PENDENTE",
                requesting_user_id=1002
            )

        self.repository.get_user_by_id.assert_not_called()
        self.repository.update_user_status.assert_not_called()

    # 36. Não permitir alterar para o mesmo status
    def test_nao_alterar_para_mesmo_status(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        with self.assertRaisesRegex(ValueError, "já possui esse status"):
            self.service.update_user_status(
                user_id=1000,
                new_status="ATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()


    # 37. Não permitir transição de status inválida
    def test_nao_permitir_transicao_status_invalida(self):

        usuario = copy.deepcopy(self.usuario_excluido)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        with self.assertRaisesRegex(ValueError, "Não é permitido alterar"):
            self.service.update_user_status(
                user_id=1000,
                new_status="INATIVO",
                requesting_user_id=1002
            )

        self.repository.update_user_status.assert_not_called()


    # 38. Deve retornar o tipo de usuário quando ele existir
    def test_consultar_tipo_usuario_com_sucesso(self):

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        resultado = self.service.get_user_type(2)

        self.assertEqual(resultado["id"], 2)
        self.assertEqual(resultado["descricao"], "USER")

        self.repository.get_user_type_by_id.assert_called_once_with(2)


    # 39. Deve gerar erro quando o tipo não existir
    def test_consultar_tipo_usuario_inexistente(self):

        self.repository.get_user_type_by_id.return_value = None

        with self.assertRaises(ValueError):
            self.service.get_user_type(99)

        self.repository.get_user_type_by_id.assert_called_once_with(99)


    # 40. Deve rejeitar um ID inválido
    def test_consultar_tipo_usuario_com_id_invalido(self):

        with self.assertRaises(ValueError):
            self.service.get_user_type(0)

        self.repository.get_user_type_by_id.assert_not_called()



    # 41. Administrador atualiza os dados de outro usuário
    def test_administrador_atualizar_usuario_com_sucesso(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_cpf.return_value = None
        self.repository.update_user.side_effect = lambda user: user

        result = self.service.update_user_profile(
            user_id=1000,
            requesting_user_id=1002,
            nome_completo="João Atualizado",
            email="joao.novo@email.com",
            cpf="111.444.777-35"
        )

        self.assertEqual(result.nome_completo, "João Atualizado")
        self.assertEqual(result.email, "joao.novo@email.com")
        self.assertEqual(result.cpf, "11144477735")

        self.repository.update_user.assert_called_once_with(usuario)


    # 42. Usuário comum atualiza o próprio cadastro
    def test_usuario_atualizar_proprio_cadastro(self):

        usuario = copy.deepcopy(self.usuario_criado)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            usuario
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_cpf.return_value = None
        self.repository.update_user.side_effect = lambda user: user

        result = self.service.update_user_profile(
            user_id=1000,
            requesting_user_id=1000,
            nome_completo="João Atualizado",
            email="joao.novo@email.com",
            cpf="111.444.777-35"
        )

        self.assertEqual(result.nome_completo, "João Atualizado")
        self.assertEqual(result.email, "joao.novo@email.com")
        self.assertEqual(result.cpf, "11144477735")

        self.repository.update_user.assert_called_once_with(usuario)


    # 43. Usuário comum não pode atualizar outro cadastro
    def test_usuario_nao_atualizar_cadastro_de_outro(self):

        usuario = copy.deepcopy(self.usuario_criado)
        solicitante = copy.deepcopy(self.usuario_inativo)
        solicitante.status = "ATIVO"

        self.repository.get_user_by_id.side_effect = [
            usuario,
            solicitante
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        with self.assertRaisesRegex(
            ValueError,
            "só podem alterar o próprio cadastro"
        ):
            self.service.update_user_profile(
                user_id=1000,
                requesting_user_id=1001,
                nome_completo="João Atualizado",
                email="joao.novo@email.com",
                cpf="111.444.777-35"
            )

        self.repository.update_user.assert_not_called()


    # 44. Não permitir e-mail já cadastrado para outro usuário
    def test_nao_atualizar_usuario_com_email_duplicado(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)
        outro_usuario = copy.deepcopy(self.usuario_inativo)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.get_user_by_email.return_value = outro_usuario

        with self.assertRaisesRegex(
            ValueError,
            "e-mail já está cadastrado"
        ):
            self.service.update_user_profile(
                user_id=1000,
                requesting_user_id=1002,
                nome_completo="João da Silva",
                email="maria@email.com",
                cpf="529.982.247-25"
            )

        self.repository.update_user.assert_not_called()


    # 45. Não permitir CPF já cadastrado para outro usuário
    def test_nao_atualizar_usuario_com_cpf_duplicado(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)
        outro_usuario = copy.deepcopy(self.usuario_inativo)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 1,
            "descricao": "ADMIN"
        }

        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_cpf.return_value = outro_usuario

        with self.assertRaisesRegex(
            ValueError,
            "CPF já está cadastrado"
        ):
            self.service.update_user_profile(
                user_id=1000,
                requesting_user_id=1002,
                nome_completo="João da Silva",
                email="joao.novo@email.com",
                cpf="111.444.777-35"
            )

        self.repository.update_user.assert_not_called()


    # 46. Administrador altera o tipo de usuário
    def test_administrador_alterar_tipo_usuario(self):

        usuario = copy.deepcopy(self.usuario_criado)
        administrador = copy.deepcopy(self.administrador)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            administrador
        ]

        self.repository.get_user_type_by_id.side_effect = [
            {"id": 1, "descricao": "ADMIN"},
            {"id": 1, "descricao": "ADMIN"},
            {"id": 1, "descricao": "ADMIN"}
        ]

        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_cpf.return_value = None
        self.repository.update_user.side_effect = lambda user: user

        result = self.service.update_user_profile(
            user_id=1000,
            requesting_user_id=1002,
            nome_completo="João da Silva",
            email="joao@email.com",
            cpf="529.982.247-25",
            tipo_usuario_id=1
        )

        self.assertEqual(result.tipo_usuario_id, 1)
        self.repository.update_user.assert_called_once_with(usuario)


    # 47. Usuário comum não pode alterar o tipo de usuário
    def test_usuario_nao_alterar_tipo_usuario(self):

        usuario = copy.deepcopy(self.usuario_criado)

        self.repository.get_user_by_id.side_effect = [
            usuario,
            usuario
        ]

        self.repository.get_user_type_by_id.return_value = {
            "id": 2,
            "descricao": "USER"
        }

        with self.assertRaisesRegex(
            ValueError,
            "não podem alterar o tipo de usuário"
        ):
            self.service.update_user_profile(
                user_id=1000,
                requesting_user_id=1000,
                nome_completo="João da Silva",
                email="joao@email.com",
                cpf="529.982.247-25",
                tipo_usuario_id=1
            )

        self.repository.update_user.assert_not_called()





if __name__ == "__main__":
    unittest.main()
