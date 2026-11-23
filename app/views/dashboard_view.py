from tkinter import ttk

from app.utils.window_utils import center_window
from app.utils.theme import apply_theme, COLORS


class DashboardView:

    def __init__(
        self,
        root,
        user,
        user_type,
        on_logout,
        on_manage_users
    ):
        self.root = root
        self.user = user
        self.user_type = user_type
        self.on_logout = on_logout
        self.on_manage_users = on_manage_users

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.root.title("UserFlow — Painel Principal")
        self.root.minsize(720, 520)
        center_window(self.root, 920, 620)
        self.root.resizable(True, True)
        apply_theme(self.root)

    def _create_widgets(self):
        container = ttk.Frame(self.root, style="Main.TFrame", padding=28)
        container.pack(expand=True, fill="both")

        # Cabeçalho
        header = ttk.Frame(container, style="Main.TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(
            header,
            text="UserFlow",
            style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(
            header,
            text="Sair",
            style="Secondary.TButton",
            command=self.on_logout
        ).pack(side="right")

        # Card de boas-vindas e perfil
        welcome_card = ttk.Frame(container, style="Card.TFrame", padding=22)
        welcome_card.pack(fill="x", pady=(0, 20))

        ttk.Label(
            welcome_card,
            text=f"Bem-vindo, {self.user.nome_completo}",
            style="CardTitle.TLabel"
        ).pack(anchor="w")

        if self.user_type == "ADMIN":
            profile_text = "Perfil: Administrador (ADMIN) — Acesso completo à gestão de usuários, status e reativações"
            management_title = "Gerenciar usuários"
            management_desc = "Consulte cadastros, altere status, aprove reativações e edite dados."
        else:
            profile_text = "Perfil: Usuário padrão (USER) — Consulta e edição dos seus próprios dados cadastrais"
            management_title = "Meu perfil"
            management_desc = "Visualize e atualize suas informações pessoais (nome, e-mail e CPF)."

        ttk.Label(
            welcome_card,
            text=profile_text,
            style="CardSubtitle.TLabel"
        ).pack(anchor="w", pady=(6, 0))

        # Módulos disponíveis
        modules_frame = ttk.LabelFrame(
            container,
            text="Módulos do sistema",
            style="Card.TLabelframe",
            padding=20
        )
        modules_frame.pack(fill="both", expand=True)

        module_box = ttk.Frame(modules_frame, style="Card.TFrame")
        module_box.pack(fill="x", pady=(4, 14))

        ttk.Button(
            module_box,
            text=management_title,
            style="Primary.TButton",
            command=self.on_manage_users
        ).pack(anchor="w")

        ttk.Label(
            module_box,
            text=management_desc,
            style="Field.TLabel"
        ).pack(anchor="w", pady=(6, 0))

        ttk.Separator(modules_frame, orient="horizontal").pack(fill="x", pady=12)

        ttk.Label(
            modules_frame,
            text="Novos módulos e integrações podem ser acoplados nesta área conforme a evolução do sistema.",
            style="Muted.TLabel"
        ).pack(anchor="w")