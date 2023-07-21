from kivy.uix.screenmanager import Screen

class ChatScreen(Screen):
    def clear_connection(self):
        # Coloque aqui a lógica para limpar os elementos da tela de chat.
        # Por exemplo:
        self.width = 230
        self.height = 340
        self.x = Window.width - self.width
        self.y = Window.height - self.height
        self.ids.chat_richedit.text = 'AllaKore Remote - Chat\n\n'
        self.ids.your_text_edit.text = ''
        self.ids.chat_richedit.text += 'Other initializations...'.
    
