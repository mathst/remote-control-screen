from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App
import pyperclip

class MainScreen(Screen):
    
    def clear_connection(self):
        self.width = 600
        self.height = 986

    def clipboard_timer(self, dt):
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text and clipboard_text != self.old_clipboard_text:
                self.old_clipboard_text = clipboard_text
                try:
                    # Envie os dados para o servidor usando o método apropriado, como no exemplo abaixo:
                    self.main_socket.sendall(bytes[, flags])(f'[CLIPBOARD]{clipboard_text}[/CLIPBOARD]')
                except Exception as e:
                    print(f"Error sending clipboard data: {e}")
        except Exception as e:
            print(f"Error accessing clipboard: {e}")
        

    def set_connected(self):
        self.ids.your_id_edit.text = 'Receiving...'
        self.ids.your_id_edit.disabled = True

        self.ids.your_password_edit.text = 'Receiving...'
        self.ids.your_password_edit.disabled = True

        self.ids.target_id_edit.text = ''
        self.ids.target_id_edit.disabled = True

        self.ids.connect_button.disabled = True

    def set_online(self):
        self.ids.your_id_edit.text = MyID
        self.ids.your_id_edit.disabled = False

        self.ids.your_password_edit.text = MyPassword
        self.ids.your_password_edit.disabled = False

        self.ids.target_id_edit.text = ''
        self.ids.target_id_edit.disabled = False

        self.ids.connect_button.disabled = False
    

    def connect_button_click(self):
        target_id = self.ids.target_id_edit.text.strip().replace('-', '')

        if not target_id:
            return

        if target_id == MyID:  # Substitua MyID pelo valor correto
            self.show_popup('You can not connect with yourself!')
        else:
            # Enviar a ID para o socket ou fazer outras operações aqui
            # ('<|FINDID|>' + TargetID_MaskEdit.Text + '<|END|>')
            self.ids.target_id_edit.disabled = True
            self.ids.connect_button.disabled = True
            self.update_status('Finding the ID...')

    def show_popup(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        close_button = Button(text='Close')
        popup = Popup(title='', content=content, size_hint=(None, None), size=(400, 200))

        def close_popup(instance):
            popup.dismiss()

        close_button.bind(on_release=close_popup)
        content.add_widget(close_button)
        popup.open()

    def update_status(self, message):
        self.ids.status_label.text = message
        self.ids.status_image.source = 'path_to_your_image.png'  # Substitua pelo caminho correto para a imagem
        
