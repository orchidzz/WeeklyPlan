# screen configuration
# adapted from https://stackoverflow.com/questions/27234386/force-window-size-kivy
from kivy.config import Config
Config.set('graphics', 'resizable', False)  # keep the screen from being resized
Config.set('graphics', 'width',  1000)  # const screen width
Config.set('graphics', 'height', 650)  # const screen height

# other imports -- must be done after configuration
from kivy.app import App
from widgets import *


# main app whose instance is to be run
class KivyApp(App):
    # override parent's build method which is called when running the app
    def build(self):
        # calendar widget and functionalities to fill the app screen
        layout = CalendarWidget()
        return layout


if __name__ == '__main__':
    KivyApp().run()
