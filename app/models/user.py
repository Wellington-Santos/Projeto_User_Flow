from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    nome_completo: str
    email: str
    cpf: str
    senha: str
    tipo_usuario_id: int
    status: str = "ATIVO"
    data_criacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
    precisa_trocar_senha: bool = False
    solicitacao_reativacao: bool = False
    
