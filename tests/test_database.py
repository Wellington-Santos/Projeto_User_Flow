import unittest

from app.database.connection import get_connection

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        # Configura o ambiente de teste, se necessário
        self.connection = get_connection()

    def tearDown(self):
        # Limpa o ambiente de teste, se necessário
        self.connection.close()

    def test_tabela_usuarios_exists(self):
        # Testa se a tabela de usuários existe no banco de dados
        resultado = self.connection.execute("""
            SELECT name
              FROM sqlite_master
             WHERE type='table'
               AND name='usuarios';
        """).fetchone()
        self.assertIsNotNone(resultado)

    def test_tabela_tipos_usuario_exists(self):
        # Testa se a tabela de tipos de usuário existe no banco de dados
        resultado = self.connection.execute("""
            SELECT name
              FROM sqlite_master
             WHERE type='table'
               AND name='tipos_usuario';
        """).fetchone()
        self.assertIsNotNone(resultado)

    def test_perfis_iniciais_existentes(self):
        # Testa se os perfis iniciais (ADMIN e USER) existem na tabela de tipos de usuário
        resultado = self.connection.execute("""
            SELECT descricao
              FROM tipos_usuario
             WHERE descricao IN ('ADMIN', 'USER');
        """).fetchall()

        perfis = [row["descricao"] for row in resultado]
        
        self.assertIn("ADMIN", perfis)
        self.assertIn("USER", perfis)

    def test_relacionamento_usuario_tipo(self):

        resultado = self.connection.execute("""
            PRAGMA foreign_key_list(usuarios)
        """).fetchall()

        relacionamentos = [
            registro["table"] for registro in resultado
        ]

        self.assertIn("tipos_usuario", relacionamentos)