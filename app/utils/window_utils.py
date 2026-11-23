# Centraliza uma janela Tkinter na tela com base nas dimensões informadas.
def center_window(window, width, height):

    # Atualiza as informações da janela
    window.update_idletasks()

    # Obtém as dimensões do monitor
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição central
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Define tamanho e posicionamento
    window.geometry(f"{width}x{height}+{x}+{y}")