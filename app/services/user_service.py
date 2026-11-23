
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.validators import Validators
from app.database.connection import hash_password
from app.database.connection import verify_password

class UserService:

    def __init__(self, repository=None):
        self.repository = (
            repository if repository is not None
            else UserRepository()
        )


    # Cria um novo usuário após validar os dados e verificar se o e-mail e CPF já estão cadastrados.
    def create_user(self, nome_completo: str, email: str, cpf: str, senha: str, tipo_usuario_id: int, precisa_trocar_senha: bool = False):
        
        # Valida e normalizar os dados do usuário
        nome_completo = Validators.valida_nome(nome_completo)
        email = Validators.valida_email(email)
        cpf = Validators.valida_cpf(cpf)
        senha = Validators.valida_senha(senha)
        tipo_usuario_id = Validators.valida_tipo_usuario(tipo_usuario_id)

        # Gera a criptografa a senha antes de salvar
        senha_criptografada = hash_password(senha)

        # Verificar se o tipo de usuário existe.
        tipo_usuario = self.repository.get_user_type_by_id(
            tipo_usuario_id
        )

        if tipo_usuario is None:
            raise ValueError("Tipo de usuário não encontrado.")

        # Verificar se o e-mail já está cadastrado.
        usuario_email = self.repository.get_user_by_email(email)

        if usuario_email is not None:
            raise ValueError("Este e-mail já está cadastrado.")

        # Verificar se o CPF já está cadastrado.
        usuario_cpf = self.repository.get_user_by_cpf(cpf)

        if usuario_cpf is not None:
            raise ValueError("Este CPF já está cadastrado.")

        # Cria o objeto User
        user = User(
            id=None,
            nome_completo=nome_completo,
            email=email,
            cpf=cpf,
            senha=senha_criptografada,
            tipo_usuario_id=tipo_usuario_id,
            status="ATIVO",
            precisa_trocar_senha=precisa_trocar_senha,
            solicitacao_reativacao=False
        )

        # Salva o usuário no banco de dados
        return self.repository.create_user(user)


    def create_user_by_admin(
            self,
            nome_completo: str,
            email: str,
            cpf: str,
            senha: str,
            tipo_usuario_id: int,
            requesting_user_id: int
        ):

        requesting_user_id = Validators.valida_id_usuario(
            requesting_user_id
        )

        requesting_user = self.repository.get_user_by_id(
            requesting_user_id
        )

        if requesting_user is None:
            raise ValueError("Administrador solicitante não encontrado.")

        if requesting_user.status != "ATIVO":
            raise ValueError("O administrador solicitante não está ativo.")

        requesting_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )

        if requesting_type is None or requesting_type["descricao"] != "ADMIN":
            raise ValueError(
                "Apenas administradores podem cadastrar usuários."
            )

        return self.create_user(
            nome_completo=nome_completo,
            email=email,
            cpf=cpf,
            senha=senha,
            tipo_usuario_id=tipo_usuario_id,
            precisa_trocar_senha=True
        )


    # Valida e normaliza os dados de entrada
    def authenticate_user(self, email: str, senha: str):

        email = Validators.valida_email(email)

        # Consulta o usuário pelo e-mail.
        usuario = self.repository.get_user_by_email(email)

        # Verifica se o usuário existe e se a senha está correta.
        if usuario is None or not verify_password(senha, usuario.senha):
            raise ValueError("E-mail ou senha inválidos.")

        if usuario.status == "INATIVO":
            raise InactiveUserError(usuario)

        # Verifica se o usuário está ativo.
        if usuario.status != "ATIVO":
            raise ValueError("Usuário não possui acesso ativo.")

        # Consulta o tipo de usuário.
        tipo_usuario = self.repository.get_user_type_by_id(
            usuario.tipo_usuario_id
        )

        if tipo_usuario is None:
            raise ValueError("Tipo de usuário não encontrado.")

        # Permite acesso aos dois perfis.
        if tipo_usuario["descricao"] not in {"ADMIN", "USER"}:
            raise ValueError("Tipo de usuário não possui acesso ao sistema.")

        return usuario


    # Método para alterar a senha de um usuário autenticado
    def change_password(self, 
                        user_id: int, 
                        current_password: str, 
                        new_password: str):

        # Valida o ID e a nova senha
        user_id = Validators.valida_id_usuario(user_id)
        new_password = Validators.valida_senha(new_password)

        # Consulta o usuário no banco de dados.
        usuario = self.repository.get_user_by_id(user_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        # Confere se a senha atual informada está correta.
        if not verify_password(current_password, usuario.senha):
            raise ValueError("A senha atual está incorreta.")

        # Impede que o usuário reutilize a senha atual.
        if verify_password(new_password, usuario.senha):
            raise ValueError("A nova senha deve ser diferente da senha atual.")

        # Gera o hash da nova senha.
        senha_criptografada = hash_password(new_password)

        # Atualiza a senha e remove a obrigatoriedade de troca
        usuario_atualizado = self.repository.update_user_password(user_id = user_id, 
                                                                  new_password = senha_criptografada, 
                                                                  precisa_trocar_senha = False)

        if usuario_atualizado is None:
            raise ValueError("Não foi possível atualizar a senha.")

        return usuario_atualizado


    # Método que realiza consulta para buscar todos os usuários que são Inativos ou que solicitaram a reativação
    def get_pending_reactivation_requests(self):
        return self.repository.get_pending_reactivation_requests()
    

    # Método para aprovar a solicitação de troca de senha
    def approve_reactivation_request(self, user_id: int):
        
        user_id = Validators.valida_id_usuario(user_id)

        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        if user.status != "INATIVO":
            raise ValueError("Somente usuários inativos podem ser reativados.")

        if not user.solicitacao_reativacao:
            raise ValueError("O usuário não possui uma solicitação de reativação pendente.")

        updated_user = self.repository.resolve_reactivation_request(
            user_id,
            approved=True
        )

        if updated_user is None:
            raise ValueError("Não foi possível aprovar a solicitação de reativação.")

        return updated_user

    
    # Método para ralizar a negação da troca de senha
    def reject_reactivation_request(self, user_id: int):

        user_id = Validators.valida_id_usuario(user_id)

        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        if user.status != "INATIVO":
            raise ValueError("Somente usuários inativos podem ter solicitações rejeitadas.")

        if not user.solicitacao_reativacao:
            raise ValueError("O usuário não possui uma solicitação de reativação pendente.")

        updated_user = self.repository.resolve_reactivation_request(
            user_id,
            approved=False
        )

        if updated_user is None:
            raise ValueError("Não foi possível rejeitar a solicitação de reativação.")

        return updated_user


    # Consulta todos os usuários cadastrados
    def get_all_users(self, include_excluded=True):

        return self.repository.get_all_users(
            include_excluded=include_excluded
        )


    # Consulta o tipo de usuário pelo ID
    def get_user_type(self, tipo_usuario_id: int):

        tipo_usuario_id = Validators.valida_tipo_usuario(
            tipo_usuario_id
        )

        user_type = self.repository.get_user_type_by_id(
            tipo_usuario_id
        )

        if user_type is None:
            raise ValueError("Tipo de usuário não encontrado.")

        return user_type


    # Consulta o tipo de usuário pela descrição
    def get_user_type_by_description(self, description: str):

        if not isinstance(description, str):
            raise ValueError("Descrição do tipo de usuário inválida.")

        description = description.strip().upper()

        if description not in {"ADMIN", "USER"}:
            raise ValueError("Tipo de usuário inválido.")

        user_type = self.repository.get_user_type_by_description(
            description
        )

        if user_type is None:
            raise ValueError("Tipo de usuário não encontrado.")

        return user_type


    # Atualiza o status do usuário
    def update_user_status(
            self,
            user_id: int,
            new_status: str,
            requesting_user_id: int):
        
        # Valida os IDs recebidos.
        user_id = Validators.valida_id_usuario(user_id)
        requesting_user_id = Validators.valida_id_usuario(
            requesting_user_id
        )
    
        # Valida o novo status.
        if not isinstance(new_status, str):
            raise ValueError("Status inválido.")
    
        new_status = new_status.strip().upper()
    
        statuses_validos = {"ATIVO", "INATIVO", "EXCLUIDO"}
    
        if new_status not in statuses_validos:
            raise ValueError("Status informado não é permitido.")
    
        # Consulta o usuário que terá o status alterado.
        user = self.repository.get_user_by_id(user_id)
    
        if user is None:
            raise ValueError("Usuário não encontrado.")
    
        # Consulta o administrador solicitante.
        requesting_user = self.repository.get_user_by_id(
            requesting_user_id
        )
    
        if requesting_user is None:
            raise ValueError("Administrador solicitante não encontrado.")
    
        # Verifica se o solicitante está ativo.
        if requesting_user.status != "ATIVO":
            raise ValueError("O administrador solicitante não está ativo.")
    
        # Consulta o tipo de usuário do solicitante.
        requesting_user_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )
        
        # Verifica se o tipo de usuário existe.
        if requesting_user_type is None:
            raise ValueError("Tipo de usuário não encontrado.")
        
        # Verifica se o solicitante é administrador.
        if requesting_user_type["descricao"] != "ADMIN":
            raise ValueError("Apenas administradores podem alterar status.")
    
        # Impede que o administrador altere o próprio status.
        if user_id == requesting_user_id:
            raise ValueError(
                "Um administrador não pode alterar o próprio status."
            )
    
        # Impede uma atualização desnecessária.
        if user.status == new_status:
            raise ValueError("O usuário já possui esse status.")
    
        # Define as transições permitidas.
        transicoes_permitidas = {
            "ATIVO": {"INATIVO", "EXCLUIDO"},
            "INATIVO": {"ATIVO", "EXCLUIDO"},
            "EXCLUIDO": {"ATIVO"}
        }
    
        if new_status not in transicoes_permitidas[user.status]:
            raise ValueError(
                f"Não é permitido alterar o status de "
                f"{user.status} para {new_status}."
            )
    
        # Reaproveita a regra de exclusão lógica já implementada.
        if new_status == "EXCLUIDO":
            return self.delete_user(user_id, requesting_user_id)
    
        # Atualiza o status no banco.
        updated_user = self.repository.update_user_status(
            user_id,
            new_status
        )
    
        if updated_user is None:
            raise ValueError("Não foi possível atualizar o status do usuário.")
    
        return updated_user


    # Atualiza os dados cadastrais de um usuário.
    def update_user_profile(
        self,
        user_id: int,
        requesting_user_id: int,
        nome_completo: str,
        email: str,
        cpf: str,
        tipo_usuario_id: int = None
    ):

        # Valida os identificadores.
        user_id = Validators.valida_id_usuario(user_id)
        requesting_user_id = Validators.valida_id_usuario(
            requesting_user_id
        )

        # Consulta o usuário que será atualizado.
        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        # Consulta quem está solicitando a alteração.
        requesting_user = self.repository.get_user_by_id(
            requesting_user_id
        )

        if requesting_user is None:
            raise ValueError("Usuário solicitante não encontrado.")

        if requesting_user.status != "ATIVO":
            raise ValueError("O usuário solicitante não está ativo.")

        # Identifica o perfil do solicitante.
        requesting_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )

        if requesting_type is None:
            raise ValueError("Tipo de usuário não encontrado.")

        profile = requesting_type["descricao"]

        if profile not in {"ADMIN", "USER"}:
            raise ValueError("Perfil sem permissão para esta operação.")

        # Usuário comum só pode editar o próprio cadastro.
        if profile == "USER" and user_id != requesting_user_id:
            raise ValueError(
                "Usuários comuns só podem alterar o próprio cadastro."
            )

        # Valida os dados cadastrais.
        nome_completo = Validators.valida_nome(nome_completo)
        email = Validators.valida_email(email)
        cpf = Validators.valida_cpf(cpf)

        # Verifica se o e-mail pertence a outro usuário.
        email_owner = self.repository.get_user_by_email(email)

        if email_owner is not None and email_owner.id != user_id:
            raise ValueError("Este e-mail já está cadastrado.")

        # Verifica se o CPF pertence a outro usuário.
        cpf_owner = self.repository.get_user_by_cpf(cpf)

        if cpf_owner is not None and cpf_owner.id != user_id:
            raise ValueError("Este CPF já está cadastrado.")

        # Usuários comuns não podem alterar o próprio tipo.
        if profile == "USER" and tipo_usuario_id is not None:
            raise ValueError(
                "Usuários comuns não podem alterar o tipo de usuário."
            )

        # Administradores podem alterar o tipo de usuário.
        if profile == "ADMIN" and tipo_usuario_id is not None:

            tipo_usuario_id = Validators.valida_tipo_usuario(
                tipo_usuario_id
            )

            tipo_usuario = self.repository.get_user_type_by_id(
                tipo_usuario_id
            )

            if tipo_usuario is None:
                raise ValueError("Tipo de usuário não encontrado.")

            user.tipo_usuario_id = tipo_usuario_id

        # Atualiza somente os dados permitidos.
        user.nome_completo = nome_completo
        user.email = email
        user.cpf = cpf

        updated_user = self.repository.update_user(user)

        if updated_user is None:
            raise ValueError("Não foi possível atualizar os dados do usuário.")

        return updated_user


    # Define uma senha temporária para outro usuário.
    def set_temporary_password(
        self,
        user_id: int,
        requesting_user_id: int,
        temporary_password: str
    ):

        # Valida os identificadores.
        user_id = Validators.valida_id_usuario(user_id)
        requesting_user_id = Validators.valida_id_usuario(
            requesting_user_id
        )

        # Impede que o administrador defina a própria senha
        # por este fluxo administrativo.
        if user_id == requesting_user_id:
            raise ValueError(
                "Não é permitido definir uma senha temporária para a própria conta."
            )

        # Consulta o usuário que receberá a senha.
        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        # Consulta o administrador solicitante.
        requesting_user = self.repository.get_user_by_id(
            requesting_user_id
        )

        if requesting_user is None:
            raise ValueError("Administrador solicitante não encontrado.")

        if requesting_user.status != "ATIVO":
            raise ValueError("O administrador solicitante não está ativo.")

        # Verifica o perfil do solicitante.
        requesting_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )

        if requesting_type is None:
            raise ValueError("Tipo de usuário não encontrado.")

        if requesting_type["descricao"] != "ADMIN":
            raise ValueError(
                "Apenas administradores podem definir senhas temporárias."
            )

        # Valida a senha temporária.
        temporary_password = Validators.valida_senha(
            temporary_password
        )

        # Impede reutilização da senha atual.
        if verify_password(temporary_password, user.senha):
            raise ValueError(
                "A senha temporária deve ser diferente da senha atual."
            )

        # Gera o hash da senha.
        encrypted_password = hash_password(temporary_password)

        # Atualiza a senha exigindo troca no próximo login.
        updated_user = self.repository.update_user_password(
            user_id=user_id,
            new_password=encrypted_password,
            precisa_trocar_senha=True
        )

        if updated_user is None:
            raise ValueError(
                "Não foi possível definir a senha temporária."
            )

        return updated_user


    # Consulta o usuario pelo ID
    def get_user_by_id(self, user_id: int, requesting_user_id: int):

        user_id = Validators.valida_id_usuario(user_id)
        requesting_user_id = Validators.valida_id_usuario(requesting_user_id)

        requesting_user = self.repository.get_user_by_id(
            requesting_user_id
        )

        if requesting_user is None:
            raise ValueError("Usuário solicitante não encontrado.")

        if requesting_user.status != "ATIVO":
            raise ValueError("Usuário solicitante não está ativo.")

        requesting_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )

        if requesting_type is None:
            raise ValueError("Tipo de usuário não encontrado.")

        is_admin = requesting_type["descricao"] == "ADMIN"

        if not is_admin and user_id != requesting_user_id:
            raise ValueError(
                "Você não tem permissão para consultar este usuário."
            )

        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        return user


    # Realiza a requisição de reativação do usuário Inativo
    def request_reactivation(self, user_id: int):

        user_id = Validators.valida_id_usuario(user_id)

        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        if user.status != "INATIVO":
            raise ValueError(
                "Somente usuários inativos podem solicitar reativação."
            )

        if user.solicitacao_reativacao:
            raise ValueError(
                "Já existe uma solicitação de reativação pendente."
            )

        result = self.repository.request_reactivation(user_id)

        if result is None:
            raise ValueError(
                "Não foi possível registrar a solicitação de reativação."
            )

        return result


    # Método para realizar a exclusão lógica de um usuário
    # Obs.: Somente administradores ativos podem excluir usuários.
    #       Um administrador não pode excluir a própria conta
    def delete_user(self, user_id: int, requesting_user_id: int):
         # 1. Validar os IDs recebidos.
        user_id = Validators.valida_id_usuario(user_id)
        requesting_user_id = Validators.valida_id_usuario(requesting_user_id)

        # 2. Consultar o usuário que será excluído.
        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        # 3. Consultar o administrador responsável pela operação.
        requesting_user = self.repository.get_user_by_id(requesting_user_id)

        if requesting_user is None:
            raise ValueError("Administrador solicitante não encontrado.")

        # 4. Verificar se o solicitante está ativo.
        if requesting_user.status != "ATIVO":
            raise ValueError("Somente administradores ativos podem excluir usuários.")

        # 5. Verificar se o solicitante possui perfil ADMIN.
        user_type = self.repository.get_user_type_by_id(
            requesting_user.tipo_usuario_id
        )

        if user_type is None or user_type["descricao"] != "ADMIN":
            raise ValueError("Apenas administradores podem excluir usuários.")

        # 6. Impedir que o administrador exclua a própria conta.
        if user_id == requesting_user_id:
            raise ValueError("Você não pode excluir sua própria conta.")

        # 7. Verificar se o usuário já foi excluído.
        if user.status == "EXCLUIDO":
            raise ValueError("Este usuário já foi excluído.")

        # 8. Executar a exclusão lógica no Repository.
        deleted_user = self.repository.delete_user(user_id)

        if deleted_user is None:
            raise ValueError(
                "Não foi possível excluir o usuário. "
                "Verifique se o registro ainda está disponível."
            )

        return deleted_user


class InactiveUserError(ValueError):

    def __init__(self, user):
        self.user = user

        super().__init__(
            "Usuário não possui acesso ativo."
        )