import tkinter as tk
from tkinter import ttk, messagebox

from app.utils.window_utils import center_window
from app.utils.theme import apply_theme
from app.services.user_service import InactiveUserError


class LoginView:

    def __init__(self, root, user_service, on_login_success):
        self.root = root
        self.user_service = user_service
        self.on_login_success = on_login_success

        self.root.title("UserFlow — Acesso ao Sistema")
        self.root.minsize(420, 470)
        center_window(self.root, 420, 470)
        self.root.resizable(False, False)

        apply_theme(self.root)
        self._create_widgets()

    def _create_widgets(self):
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=24)
        outer.pack(expand=True, fill="both")

        card = ttk.Frame(outer, style="Card.TFrame", padding=28)
        card.pack(expand=True, fill="both")

        ttk.Label(
            card,
            text="UserFlow",
            style="CardTitle.TLabel"
        ).pack(pady=(6, 4))

        ttk.Label(
            card,
            text="Gestão de Usuários e Controle de Acesso",
            style="CardSubtitle.TLabel"
        ).pack(pady=(0, 24))

        ttk.Label(
            card,
            text="E-mail",
            style="Field.TLabel"
        ).pack(anchor="w")

        self.email_entry = ttk.Entry(card, style="App.TEntry", width=40)
        self.email_entry.pack(fill="x", pady=(5, 14))

        ttk.Label(
            card,
            text="Senha",
            style="Field.TLabel"
        ).pack(anchor="w")

        self.password_entry = ttk.Entry(
            card,
            style="App.TEntry",
            width=40,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(5, 22))

        self.login_button = ttk.Button(
            card,
            text="Entrar",
            style="Primary.TButton",
            command=self._login
        )
        self.login_button.pack(fill="x")

        self.root.bind("<Return>", lambda event: self._login())
        self.email_entry.focus_set()

    def _login(self):
        email = self.email_entry.get().strip()
        senha = self.password_entry.get().strip()

        if not email or not senha:
            messagebox.showwarning(
                "Atenção",
                "Informe o e-mail e a senha para continuar."
            )
            return

        self.login_button.config(state="disabled")

        try:
            user = self.user_service.authenticate_user(email, senha)

            if user is None:
                messagebox.showerror(
                    "Falha na autenticação",
                    "E-mail ou senha inválidos."
                )
                return

            self.on_login_success(user)

        except InactiveUserError as error:
            user = error.user

            confirmed = messagebox.askyesno(
                "Conta inativa",
                "Sua conta está inativa.\n\n"
                "Deseja solicitar a reativação do seu acesso?"
            )

            if confirmed:
                try:
                    self.user_service.request_reactivation(user.id)
                    messagebox.showinfo(
                        "Solicitação enviada",
                        "Sua solicitação de reativação foi registrada.\n"
                        "Aguarde a análise de um administrador."
                    )
                except ValueError as request_error:
                    messagebox.showwarning(
                        "Solicitação não realizada",
                        str(request_error)
                    )

        except ValueError as error:
            messagebox.showerror("Falha na autenticação", str(error))

        except Exception:
            messagebox.showerror(
                "Erro",
                "Não foi possível realizar o login. Tente novamente."
            )

        finally:
            if self.root.winfo_exists():
                self.login_button.config(state="normal")