from kivy.app import App
from kivy.uix.button import Button

class MiaApp(App):
    def build(self):
        return Button(text="Ciao Android!")

MiaApp().run()
