from tkinter import ttk, messagebox

from app.utils.window_utils import center_window
from app.utils.theme import apply_theme


class ChangePasswordView:

    def __init__(self, root, user, user_service, on_password_changed):
        self.root = root
        self.user = user
        self.user_service = user_service
        self.on_password_changed = on_password_changed

        self.root.title("UserFlow — Alteração de Senha")
        self.root.geometry("430x510")
        center_window(self.root, 430, 510)
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
            text="Alteração de Senha",
            style="CardTitle.TLabel"
        ).pack(pady=(6, 6))

        ttk.Label(
            card,
            text="Defina uma nova senha para prosseguir com segurança.",
            style="CardSubtitle.TLabel",
            wraplength=340
        ).pack(pady=(0, 22))

        ttk.Label(
            card,
            text="Senha atual",
            style="Field.TLabel"
        ).pack(anchor="w")

        self.current_password_entry = ttk.Entry(
            card,
            style="App.TEntry",
            show="*"
        )
        self.current_password_entry.pack(fill="x", pady=(5, 14))

        ttk.Label(
            card,
            text="Nova senha",
            style="Field.TLabel"
        ).pack(anchor="w")

        self.new_password_entry = ttk.Entry(
            card,
            style="App.TEntry",
            show="*"
        )
        self.new_password_entry.pack(fill="x", pady=(5, 14))

        ttk.Label(
            card,
            text="Confirmar nova senha",
            style="Field.TLabel"
        ).pack(anchor="w")

        self.confirm_password_entry = ttk.Entry(
            card,
            style="App.TEntry",
            show="*"
        )
        self.confirm_password_entry.pack(fill="x", pady=(5, 22))

        self.save_button = ttk.Button(
            card,
            text="Salvar nova senha",
            style="Primary.TButton",
            command=self._change_password
        )
        self.save_button.pack(fill="x")

        self.current_password_entry.focus_set()

    def _change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not current_password or not new_password or not confirm_password:
            messagebox.showwarning(
                "Atenção",
                "Preencha todos os campos obrigatórios."
            )
            return

        if new_password != confirm_password:
            messagebox.showerror(
                "Erro de validação",
                "A confirmação da nova senha não corresponde à nova senha."
            )
            return

        self.save_button.config(state="disabled")

        try:
            updated_user = self.user_service.change_password(
                user_id=self.user.id,
                current_password=current_password,
                new_password=new_password
            )

            messagebox.showinfo(
                "Sucesso",
                "Senha alterada com sucesso."
            )

            self.on_password_changed(updated_user)

        except ValueError as error:
            messagebox.showerror("Não foi possível alterar a senha", str(error))

        except Exception:
            messagebox.showerror(
                "Erro",
                "Ocorreu um erro ao alterar a senha. Tente novamente."
            )

        finally:
            if self.save_button.winfo_exists():
                self.save_button.config(state="normal")