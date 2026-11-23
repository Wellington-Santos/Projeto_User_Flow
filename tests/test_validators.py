import unittest

from app.services.validators import Validators

class TestValidators(unittest.TestCase):

    # Testa a validação e normalização do nome completo do usuário.
    def test_validar_nome(self):
        resultado = Validators.valida_nome(" João da Silva ")
        self.assertEqual(resultado, "João da Silva")

    # Testa a validação do nome vazio
    def test_validar_nome_vazio(self):
        with self.assertRaises(ValueError):
            Validators.valida_nome(" ")

    # Testa a validação do nome curto 
    def test_validar_nome_curto(self):
        with self.assertRaises(ValueError):
            Validators.valida_nome("Jo")

    # Testa a validação do email do usuário
    def test_validar_email(self):
        resultado = Validators.valida_email("TESTE@exemple.com")
        self.assertEqual(resultado, "teste@exemple.com")

    # Testa a validação do email inválido
    def test_validar_email_invalido(self):
        with self.assertRaises(ValueError):
            Validators.valida_email("email_invalido")

    # Testa a validação do CPF do usuário
    def test_validar_cpf(self):
        resultado = Validators.valida_cpf("529.982.247-25")
        self.assertEqual(resultado, "52998224725")

    # Testa a validação do CPF inválido
    def test_cpf_invalido(self):
        with self.assertRaises(ValueError):
            Validators.valida_cpf("111.111.111-11")

    # Testa a validação da senha
    def test_validar_senha(self):
        resultado = Validators.valida_senha("Senha123")
        self.assertEqual(resultado, "Senha123")

    # Testa a validação da senha curta
    def test_senha_curta(self):
        with self.assertRaises(ValueError):
            Validators.valida_senha("123")


if __name__ == "__main__":
    unittest.main()
