import re

from email_validator import validate_email, EmailNotValidError
from validate_docbr import CPF


# Classe para validação de dados do usuário
class Validators:

    # Valida e normaliza o nome completo do usuário
    @staticmethod
    def valida_nome(nome: str) -> bool:

        if not nome or not nome.strip():
            raise ValueError("O nome é obrigatório.")

        # Remove espaços extras e normaliza o nome
        nome = " ".join(nome.strip().split())  

        if len(nome) < 3:
            raise ValueError("O nome completo deve ter pelo menos 3 caracteres.")

        if not all(part.isalpha() for part in nome.split()):
            raise ValueError("O nome completo deve conter apenas letras.")

        return nome


    # Valida e normaliza o e-mail do usuário
    @staticmethod
    def valida_email(email: str) -> str:

        if not email or not email.strip():
            raise ValueError("O e-mail é obrigatório.")

        # Normaliza o e-mail 
        email = email.strip().lower()  

        try:
            resultado = validate_email(email, check_deliverability=False)
            
            return resultado.normalized
        
        except EmailNotValidError:
            raise ValueError("E-mail inválido.")


    # Valida o CPF do usuário e retorna somente os números
    @staticmethod
    def valida_cpf(cpf: str) -> str:

        if not cpf or not cpf.strip():
            raise ValueError("O CPF é obrigatório.")

        cpf = cpf.strip()
        cpf_validator = CPF()

        if not cpf_validator.validate(cpf):
            raise ValueError("CPF inválido.")

        return re.sub(r"\D", "", cpf)  # Remove caracteres não numéricos e


    # Valida os requisitos mínimos da senha
    @staticmethod
    def valida_senha(senha: str) -> str:

        if not isinstance(senha, str) or not senha:
            raise ValueError("A senha é obrigatória.")

        if len(senha) < 8:
            raise ValueError(
                "A senha deve possuir pelo menos 8 caracteres."
            )

        return senha


    # Valida o tipo de usuário (ID do perfil)
    @staticmethod
    def valida_tipo_usuario(tipo_usuario_id: int) -> int:

        if not isinstance(tipo_usuario_id, int) or isinstance(tipo_usuario_id, bool) or tipo_usuario_id <= 0:
            raise ValueError("Tipo de usuário inválido.")

        return tipo_usuario_id


    # Valida o status do usuário
    @staticmethod
    def valida_status(status: str) -> str:

        status_permitidos = (
            "ATIVO",
            "INATIVO",
            "EXCLUIDO"
        )

        if not isinstance(status, str):
            raise ValueError("Status inválido.")

        status = status.strip().upper()

        if status not in status_permitidos:
            raise ValueError("Status de usuário inválido.")

        return status


    # Valida o identificador do usuário
    @staticmethod
    def valida_id_usuario(user_id: int) -> int:

        if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
            raise ValueError("Identificador do usuário inválido.")        

        return user_id