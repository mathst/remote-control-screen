from kivy.uix.screenmanager import Screen
import os

class FileShareScreen(Screen):
    def clear_connection(self):
        # Coloque aqui a lógica para limpar os elementos da tela de compartilhamento de arquivos.
        # Por exemplo:

        # Verificar o sistema operacional
        if os.name == 'posix':  # Linux
            default_directory = '/'
        elif os.name == 'nt':  # Windows
            default_directory = 'C:\\'
        else:
            default_directory = os.getcwd()  # Diretório atual caso seja outro sistema operacional

        self.ids.download_bitbtn.disabled = False
        self.ids.upload_bitbtn.disabled = False
        self.ids.download_progressbar.value = 0
        self.ids.upload_progressbar.value = 0
        self.ids.size_download_label.text = 'Size: 0 B / 0 B'
        self.ids.size_upload_label.text = 'Size: 0 B / 0 B'
        self.ids.directory_edit.text = default_directory
        self.ids.sharefiles_listview.adapter.data.clear()
