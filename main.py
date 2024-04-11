from kivy.app import App
from kivy.uix.button import Button
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
from requests.auth import HTTPBasicAuth
import os
from kivy.uix.scrollview import ScrollView

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from kivy.core.window import Window

load_dotenv()
username = os.getenv('bc_username')
user_password = os.getenv('bc_password')
url = os.getenv('bc_url')

def get_data():
    response = requests.get(url, auth=HTTPBasicAuth(username, user_password))
    if response.status_code == 200:
        # Process the data
        data = response.json()
        body = ""
        finallist = []
        for row in data['value']:
            #if row['Status'] == 'In Process':
            if row['Status'] == 'Error':
                #body += f"{row['Object_Caption_to_Run']} - {row['Description']}\n{row['Error_Message']}"
                finallist.append([row['Object_Caption_to_Run'],row['Description'],row['Error_Message']])
    return finallist


class MyAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MyAppLayout, self).__init__(orientation='vertical', **kwargs)

        # Button at the top
        self.button = Button(text='Wyślij zapytanie', size_hint_y=None, height=50)
        self.add_widget(self.button)
        self.button.bind(on_press=self.on_button_click)

        # ScrollView for the TextInputs
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - self.button.height))
        self.inputs_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.inputs_layout.bind(minimum_height=self.inputs_layout.setter('height'))

        # Initial instruction TextInput
        self.text_input = TextInput(text='Nacisni przycisk wyżej, by wczytać dane...', readonly=True, halign="left", size_hint_y=None, height=50)
        self.inputs_layout.add_widget(self.text_input)

        self.scroll_view.add_widget(self.inputs_layout)
        self.add_widget(self.scroll_view)

    def on_button_click(self, instance):
        # Clear existing TextInputs except the first one
        self.inputs_layout.clear_widgets()
        self.inputs_layout.add_widget(self.text_input)  # Re-add the instruction text input

        # Fetch data and create a new TextInput for each item
        data = get_data()
        if data:
            for item in data:
                text_content = f"Nazwa: {item[0]}\nOpis: {item[1]}\nBłąd: {item[2]}"
                new_text_input = TextInput(text=text_content, readonly=True, halign="left", size_hint_y=None, height=150)
                self.inputs_layout.add_widget(new_text_input)
        else:
            text_content = f"Brak błędów - możesz zjeść ciastko"
            new_text_input = TextInput(text=text_content, readonly=True, halign="left", size_hint_y=None, height=150)
            self.inputs_layout.add_widget(new_text_input)
            




class TestApp(App):
    def build(self):
        return MyAppLayout()

if __name__ == '__main__':
    TestApp().run()
