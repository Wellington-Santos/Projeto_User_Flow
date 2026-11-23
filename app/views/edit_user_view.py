import tkinter as tk
from tkinter import ttk, messagebox

from app.utils.window_utils import center_window
from app.utils.theme import apply_theme


class EditUserView:

    def __init__(
        self,
        root,
        user,
        user_service,
        on_back,
        selected_user=None,
        mode="edit"
    ):
        self.root = root
        self.user = user
        self.user_service = user_service
        self.on_back = on_back
        self.selected_user = selected_user
        self.mode = mode

        self.user_type = self.user_service.get_user_type(
            self.user.tipo_usuario_id
        )

        self.is_admin = (
            self.user_type is not None
            and self.user_type["descricao"] == "ADMIN"
        )

        self._validate_permissions()
        self._configure_window()
        self._create_widgets()

        if self.mode == "edit":
            self._load_user_data()

    def _validate_permissions(self):
        if self.mode not in {"create", "edit"}:
            raise ValueError("Modo de operação inválido.")

        if self.mode == "create" and not self.is_admin:
            raise ValueError("Somente administradores podem cadastrar usuários.")

        if self.mode == "edit" and self.selected_user is None:
            raise ValueError("Nenhum usuário foi selecionado para edição.")

        if (
            self.mode == "edit"
            and not self.is_admin
            and self.selected_user.id != self.user.id
        ):
            raise ValueError("Você não pode editar outro usuário.")

    def _configure_window(self):
        title = "Cadastrar usuário" if self.mode == "create" else "Editar usuário"
        self.root.title(f"UserFlow — {title}")
        center_window(self.root, 560, 660)
        self.root.minsize(520, 620)
        self.root.resizable(False, False)
        apply_theme(self.root)

    def _create_widgets(self):
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=24)
        outer.pack(expand=True, fill="both")

        card = ttk.Frame(outer, style="Card.TFrame", padding=24)
        card.pack(expand=True, fill="both")

        title = "Cadastrar novo usuário" if self.mode == "create" else "Editar cadastro"

        ttk.Label(
            card,
            text=title,
            style="CardTitle.TLabel"
        ).pack(anchor="w", pady=(0, 18))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")

        self.entries = {}
        fields = [
            ("nome", "Nome completo"),
            ("email", "E-mail"),
            ("cpf", "CPF"),
        ]

        for key, label in fields:
            ttk.Label(
                form,
                text=label,
                style="Field.TLabel"
            ).pack(anchor="w", pady=(8, 3))

            entry = ttk.Entry(form, style="App.TEntry")
            entry.pack(fill="x", pady=(0, 6))
            self.entries[key] = entry

        ttk.Label(
            form,
            text="Tipo de usuário",
            style="Field.TLabel"
        ).pack(anchor="w", pady=(8, 3))

        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=("ADMIN", "USER"),
            state="readonly",
            style="App.TCombobox"
        )
        self.type_combo.pack(fill="x", pady=(0, 6))

        if not self.is_admin:
            self.type_combo.config(state="disabled")

        if self.mode == "create":
            ttk.Label(
                form,
                text="Senha temporária",
                style="Field.TLabel"
            ).pack(anchor="w", pady=(8, 3))

            self.password_entry = ttk.Entry(form, style="App.TEntry", show="*")
            self.password_entry.pack(fill="x", pady=(0, 6))

        if self.mode == "edit":
            status_row = ttk.Frame(form, style="Card.TFrame")
            status_row.pack(fill="x", pady=(12, 0))

            ttk.Label(
                status_row,
                text="Status atual:",
                style="FieldBold.TLabel"
            ).pack(side="left", padx=(0, 8))

            self.status_label = ttk.Label(
                status_row,
                text="-",
                style="Value.TLabel"
            )
            self.status_label.pack(side="left")

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(fill="x", side="bottom", pady=(20, 0))

        ttk.Button(
            actions,
            text="Salvar",
            style="Primary.TButton",
            command=self._save
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Voltar",
            style="Secondary.TButton",
            command=self.on_back
        ).pack(side="right")

    def _load_user_data(self):
        user = self.selected_user

        self.entries["nome"].insert(0, user.nome_completo)
        self.entries["email"].insert(0, user.email)
        self.entries["cpf"].insert(0, user.cpf)

        user_type = self.user_service.get_user_type(user.tipo_usuario_id)
        if user_type:
            self.type_var.set(user_type["descricao"])

        self.status_label.config(text=user.status)

        if not self.is_admin:
            self.type_combo.config(state="disabled")

    def _save(self):
        nome = self.entries["nome"].get()
        email = self.entries["email"].get()
        cpf = self.entries["cpf"].get()

        try:
            if self.mode == "create":
                senha = self.password_entry.get()
                tipo_descricao = self.type_var.get()

                if not tipo_descricao:
                    raise ValueError("Selecione o tipo de usuário.")

                if not senha:
                    raise ValueError("Informe a senha temporária.")

                user_type = self.user_service.get_user_type_by_description(
                    tipo_descricao
                )

                self.user_service.create_user_by_admin(
                    nome_completo=nome,
                    email=email,
                    cpf=cpf,
                    senha=senha,
                    tipo_usuario_id=user_type["id"],
                    requesting_user_id=self.user.id
                )

                messagebox.showinfo(
                    "Sucesso",
                    "Usuário cadastrado com sucesso.\n"
                    "Será necessário alterar a senha no primeiro acesso."
                )

            else:
                tipo_usuario_id = None

                if self.is_admin:
                    tipo_descricao = self.type_var.get()

                    if not tipo_descricao:
                        raise ValueError("Selecione o tipo de usuário.")

                    user_type = self.user_service.get_user_type_by_description(
                        tipo_descricao
                    )
                    tipo_usuario_id = user_type["id"]

                self.user_service.update_user_profile(
                    user_id=self.selected_user.id,
                    requesting_user_id=self.user.id,
                    nome_completo=nome,
                    email=email,
                    cpf=cpf,
                    tipo_usuario_id=tipo_usuario_id
                )

                messagebox.showinfo(
                    "Sucesso",
                    "Cadastro atualizado com sucesso."
                )

            self.on_back()

        except ValueError as error:
            messagebox.showwarning("Atenção", str(error))

        except Exception as error:
            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar os dados:\n{error}"
            )