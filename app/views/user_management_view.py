import tkinter as tk
from tkinter import ttk, messagebox

from app.utils.window_utils import center_window
from app.utils.theme import apply_theme, COLORS


class UserManagementView:

    def __init__(
        self,
        root,
        user,
        user_service,
        on_back,
        on_create_user,
        on_edit_user
    ):
        self.root = root
        self.user = user
        self.user_service = user_service
        self.on_back = on_back
        self.on_create_user = on_create_user
        self.on_edit_user = on_edit_user

        self.users = []
        self.status_filter = tk.StringVar(value="TODOS")

        user_type = self.user_service.get_user_type(self.user.tipo_usuario_id)
        self.is_admin = (
            user_type is not None
            and user_type["descricao"] == "ADMIN"
        )

        self._configure_window()
        self._create_widgets()
        self._load_users()

    def _configure_window(self):
        self.root.title("UserFlow — Gerenciamento de Usuários")
        center_window(self.root, 1100, 840)
        self.root.minsize(960, 740)
        self.root.resizable(True, True)
        apply_theme(self.root)

    def _create_widgets(self):
        container = ttk.Frame(self.root, style="Main.TFrame", padding=28)
        container.pack(expand=True, fill="both")

        # Cabeçalho
        header = ttk.Frame(container, style="Main.TFrame")
        header.pack(fill="x", pady=(0, 20))

        title_text = "Gerenciar usuários" if self.is_admin else "Meu cadastro"
        ttk.Label(
            header,
            text=title_text,
            style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(
            header,
            text="Voltar",
            style="Secondary.TButton",
            command=self.on_back
        ).pack(side="right", padx=(10, 0))

        if self.is_admin:
            ttk.Button(
                header,
                text="Novo usuário",
                style="Primary.TButton",
                command=self.on_create_user
            ).pack(side="right")

        # Seção de listagem e filtros
        list_card = ttk.Frame(container, style="Card.TFrame", padding=18)
        list_card.pack(fill="both", expand=True, pady=(0, 16))

        top_bar = ttk.Frame(list_card, style="Card.TFrame")
        top_bar.pack(fill="x", pady=(0, 12))

        ttk.Label(
            top_bar,
            text="Usuários cadastrados",
            style="CardTitle.TLabel"
        ).pack(side="left")

        filter_frame = ttk.Frame(top_bar, style="Card.TFrame")
        filter_frame.pack(side="right")

        ttk.Label(
            filter_frame,
            text="Filtrar por status:",
            style="Field.TLabel"
        ).pack(side="left", padx=(0, 8))

        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter,
            values=("TODOS", "ATIVO", "INATIVO", "EXCLUIDO"),
            state="readonly",
            style="App.TCombobox",
            width=15
        )
        if not self.is_admin:
            status_combo.config(state="disabled")
        status_combo.pack(side="left")
        status_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._apply_status_filter()
        )

        # Tabela
        table_frame = ttk.Frame(list_card, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "nome", "email", "status")
        self.requests_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="App.Treeview"
        )

        self.requests_tree.tag_configure("ATIVO", foreground=COLORS["success"])
        self.requests_tree.tag_configure("INATIVO", foreground=COLORS["warning"])
        self.requests_tree.tag_configure("EXCLUIDO", foreground=COLORS["danger"])

        self.requests_tree.configure(height=9)
        self.requests_tree.bind("<<TreeviewSelect>>", self._on_user_selected)

        self.requests_tree.heading("id", text="ID")
        self.requests_tree.heading("nome", text="Nome completo")
        self.requests_tree.heading("email", text="E-mail")
        self.requests_tree.heading("status", text="Status")

        self.requests_tree.column("id", width=70, anchor="center")
        self.requests_tree.column("nome", width=320)
        self.requests_tree.column("email", width=320)
        self.requests_tree.column("status", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.requests_tree.yview
        )
        self.requests_tree.configure(yscrollcommand=scrollbar.set)

        self.requests_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Detalhes do usuário selecionado
        details_frame = ttk.LabelFrame(
            container,
            text="Detalhes do usuário selecionado",
            style="Card.TLabelframe",
            padding=16
        )
        details_frame.pack(fill="x")

        self.detail_labels = {}
        fields = {
            "nome": "Nome completo:",
            "email": "E-mail:",
            "cpf": "CPF:",
            "tipo": "Tipo de usuário:",
            "status": "Status:",
            "reativacao": "Solicitação de reativação:",
        }

        for row, (key, label_text) in enumerate(fields.items()):
            ttk.Label(
                details_frame,
                text=label_text,
                style="FieldBold.TLabel"
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=3
            )

            value_label = ttk.Label(
                details_frame,
                text="-",
                style="Value.TLabel"
            )
            value_label.grid(
                row=row,
                column=1,
                sticky="w",
                pady=3
            )
            self.detail_labels[key] = value_label

        # Barra de ações
        actions_frame = ttk.Frame(container, style="Main.TFrame")
        actions_frame.pack(fill="x", pady=(18, 0))

        self.btn_edit_user = ttk.Button(
            actions_frame,
            text="Editar usuário",
            style="Primary.TButton",
            command=self._edit_selected_user
        )
        self.btn_edit_user.pack(side="left", padx=(0, 10))

        self.btn_approve = ttk.Button(
            actions_frame,
            text="Aprovar reativação",
            style="Secondary.TButton",
            command=self._approve_request,
            state="disabled"
        )
        self.btn_approve.pack(side="left", padx=(0, 10))

        self.btn_reject = ttk.Button(
            actions_frame,
            text="Rejeitar reativação",
            style="Secondary.TButton",
            command=self._reject_request,
            state="disabled"
        )
        self.btn_reject.pack(side="left", padx=(0, 10))

        self.btn_change_status = ttk.Button(
            actions_frame,
            text="Alterar status",
            style="Secondary.TButton",
            command=self._change_user_status,
            state="disabled"
        )
        self.btn_change_status.pack(side="left", padx=(0, 10))

        self.btn_delete_user = ttk.Button(
            actions_frame,
            text="Excluir usuário",
            style="Secondary.TButton",
            command=self._delete_user,
            state="disabled"
        )
        self.btn_delete_user.pack(side="left", padx=(0, 10))

        ttk.Button(
            actions_frame,
            text="Atualizar lista",
            style="Secondary.TButton",
            command=self._load_users
        ).pack(side="right")

    def _load_users(self):
        try:
            if self.is_admin:
                self.users = self.user_service.get_all_users(
                    include_excluded=True
                )
            else:
                user = self.user_service.get_user_by_id(
                    user_id=self.user.id,
                    requesting_user_id=self.user.id
                )
                self.users = [user]

            self._apply_status_filter()

            if not self.users:
                messagebox.showinfo(
                    "Usuários",
                    "Não existem usuários cadastrados."
                )

        except Exception as error:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os usuários.\n{error}"
            )

    def _on_user_selected(self, event=None):
        selected = self.requests_tree.selection()
        if not selected:
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])

        user = next((u for u in self.users if u.id == user_id), None)
        if user is None:
            return

        try:
            user_type = self.user_service.get_user_type(user.tipo_usuario_id)

            self.detail_labels["nome"].config(text=user.nome_completo)
            self.detail_labels["email"].config(text=user.email)
            self.detail_labels["cpf"].config(text=user.cpf)
            self.detail_labels["tipo"].config(
                text=user_type["descricao"] if user_type else "-"
            )
            self.detail_labels["status"].config(text=user.status)
            self.detail_labels["reativacao"].config(
                text="Pendente" if user.solicitacao_reativacao else "Não solicitada"
            )

            self._update_action_buttons(user)

            can_change_status = self.is_admin and user.id != self.user.id
            self.btn_change_status.config(
                state="normal" if can_change_status else "disabled"
            )

            if user.status == "ATIVO":
                self.btn_change_status.config(text="Inativar usuário")
            else:
                self.btn_change_status.config(text="Reativar usuário")

            can_delete = (
                self.is_admin
                and user.id != self.user.id
                and user.status != "EXCLUIDO"
            )
            self.btn_delete_user.config(
                state="normal" if can_delete else "disabled"
            )

        except ValueError as error:
            messagebox.showerror("Erro", str(error))

    def _apply_status_filter(self):
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)

        selected_status = self.status_filter.get()

        for label in self.detail_labels.values():
            label.config(text="-")

        for user in self.users:
            if selected_status != "TODOS" and user.status != selected_status:
                continue

            self.requests_tree.insert(
                "",
                "end",
                values=(user.id, user.nome_completo, user.email, user.status),
                tags=(user.status,)
            )

        self.btn_approve.config(state="disabled")
        self.btn_reject.config(state="disabled")
        self.btn_change_status.config(state="disabled")
        self.btn_delete_user.config(state="disabled")

    def _delete_user(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um usuário para excluir.")
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])
        user = next((u for u in self.users if u.id == user_id), None)
        if user is None:
            return

        confirmed = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente excluir o usuário {user.nome_completo}?\n\n"
            "Essa operação será lógica: o registro permanecerá no banco "
            "de dados, mas terá seu status alterado para EXCLUIDO."
        )
        if not confirmed:
            return

        try:
            self.user_service.delete_user(
                user_id=user.id,
                requesting_user_id=self.user.id
            )
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso.")
            self._load_users()
        except ValueError as error:
            messagebox.showerror("Erro", str(error))

    def _approve_request(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma solicitação para aprovar.")
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])

        confirmed = messagebox.askyesno(
            "Confirmar aprovação",
            "Deseja aprovar a solicitação de reativação deste usuário?"
        )
        if not confirmed:
            return

        try:
            self.user_service.approve_reactivation_request(user_id)
            messagebox.showinfo("Sucesso", "Solicitação aprovada com sucesso.")
            self._load_users()
        except ValueError as error:
            messagebox.showerror("Erro", str(error))

    def _update_action_buttons(self, user):
        has_pending_request = (
            self.is_admin
            and user.status == "INATIVO"
            and user.solicitacao_reativacao
        )
        button_state = "normal" if has_pending_request else "disabled"
        self.btn_approve.config(state=button_state)
        self.btn_reject.config(state=button_state)

    def _change_user_status(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um usuário.")
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])
        user = next((u for u in self.users if u.id == user_id), None)
        if user is None:
            return

        new_status = "INATIVO" if user.status == "ATIVO" else "ATIVO"

        confirmed = messagebox.askyesno(
            "Confirmar alteração",
            f"Deseja alterar o status do usuário para {new_status}?"
        )
        if not confirmed:
            return

        try:
            self.user_service.update_user_status(
                user_id=user.id,
                new_status=new_status,
                requesting_user_id=self.user.id
            )
            messagebox.showinfo("Sucesso", "Status alterado com sucesso.")
            self._load_users()
        except ValueError as error:
            messagebox.showerror("Erro", str(error))

    def _edit_selected_user(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])
        selected_user = next((u for u in self.users if u.id == user_id), None)

        if selected_user is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível localizar o usuário selecionado."
            )
            return

        self.on_edit_user(selected_user)

    def _reject_request(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma solicitação para rejeitar.")
            return

        values = self.requests_tree.item(selected[0], "values")
        user_id = int(values[0])

        confirmed = messagebox.askyesno(
            "Confirmar rejeição",
            "Deseja rejeitar a solicitação de reativação deste usuário?"
        )
        if not confirmed:
            return

        try:
            self.user_service.reject_reactivation_request(user_id)
            messagebox.showinfo("Sucesso", "Solicitação rejeitada com sucesso.")
            self._load_users()
        except ValueError as error:
            messagebox.showerror("Erro", str(error))