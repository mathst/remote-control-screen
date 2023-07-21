from kivy.uix.screenmanager import Screen

class ShareScreen(Screen):
    def clear_connection(self):
        # Coloque aqui a lógica para limpar os elementos da tela de controle remoto.
        self.width = 600
        self.height = 986
        self.ids.mouse_icon_image.source = 'mouse_icon_unchecked.png'
        self.ids.keyboard_icon_image.source = 'keyboard_icon_unchecked.png'
        self.ids.resize_icon_image.source = 'resize_icon_checked.png'

        self.ids.mouse_remote_checkbox.active = False
        self.ids.keyboard_remote_checkbox.active = False
        self.ids.resize_checkbox.active = True

        self.ids.screen_image.source = 'screen_start_image.png'
        
