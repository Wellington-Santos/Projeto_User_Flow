
import tkinter as tk

from app.database.connection import initialize_database
from app.services.user_service import UserService
from app.views.login_view import LoginView
from app.views.dashboard_view import DashboardView
from app.views.change_password_view import ChangePasswordView
from app.views.user_management_view import UserManagementView
from app.views.edit_user_view import EditUserView

def main():

    # Inicializa o banco de dados
    initialize_database()

    # Instancia o serviço de usuários
    user_service = UserService()

    # Cria a janela principal
    root = tk.Tk()

    # Remove os componentes da tela atual
    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()


    # Carrega a tela de login
    def show_login():

        clear_window()

        LoginView(
            root=root,
            user_service=user_service,
            on_login_success=show_after_login
        )


    # Verifica se o usuário precisa trocar a senha
    def show_after_login(user):

        if user.precisa_trocar_senha:
            show_change_password(user)
        else:
            show_dashboard(user)


    # Carrega a tela de alteração de senha
    def show_change_password(user):

        clear_window()

        ChangePasswordView(
            root=root,
            user=user,
            user_service=user_service,
            on_password_changed=show_dashboard
        )


    # Carrega o dashboard
    def show_dashboard(user):

        # Impede o acesso caso a senha ainda precise ser alterada
        if user.precisa_trocar_senha:
            show_change_password(user)
            return

        # Consulta o tipo do usuário autenticado.
        user_type = user_service.get_user_type(
            user.tipo_usuario_id
        )

        # Obtém a descrição do tipo.
        user_type_description = user_type["descricao"]

        clear_window()

        DashboardView(
            root=root,
            user=user,
            user_type=user_type_description,
            on_logout=show_login,
            on_manage_users=lambda: show_user_management(user)
        )


   # Carrega a tela de gerenciamento de usuários
    def show_user_management(user):

        # Atualiza os dados do usuário autenticado.
        current_user = user_service.get_user_by_id(
            user_id=user.id,
            requesting_user_id=user.id
        )

        clear_window()

        UserManagementView(
            root=root,
            user=current_user,
            user_service=user_service,
            on_back=lambda: show_dashboard(current_user),
            on_create_user=lambda: show_edit_user(
                current_user,
                mode="create"
            ),
            on_edit_user=lambda selected_user: show_edit_user(
                current_user,
                selected_user=selected_user,
                mode="edit"
            )
        )


    # Carrega a tela de cadastro ou edição
    def show_edit_user(user, selected_user=None, mode="edit"):
    
        clear_window()
    
        EditUserView(
            root=root,
            user=user,
            user_service=user_service,
            on_back=lambda: show_user_management(user),
            selected_user=selected_user,
            mode=mode
        )


    # Inicializa a aplicação na tela de login
    show_login()

    # Inicia o loop da interface gráfica
    root.mainloop()


if __name__ == "__main__":
    main()
