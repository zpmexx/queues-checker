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
from kivy.uix.textinput import TextInput

from kivy.core.window import Window
from kivy.clock import Clock
load_dotenv()
username = os.getenv('bc_username')
user_password = os.getenv('bc_password')
url = os.getenv('bc_url')

def get_data():
    response = requests.get(url, auth=HTTPBasicAuth(username, user_password))
    if response.status_code == 200:
        data = response.json()
        #print(len(data['value']))
        finallist = []
        numbers = []
        error, on_hold, ready, in_process = 0, 0, 0, 0
        for row in data['value']:
            if row['Status'] == 'Error':
            #if row['Status'] == 'In Process':
                finallist.append([row['Object_Caption_to_Run'], row['Description'], row['Error_Message']])
                error += 1
            elif row['Status'] == 'In Process':
                in_process += 1
            elif row['Status'] == 'Ready':
                ready += 1
            elif row['Status'] == 'On Hold':
                on_hold += 1
        numbers.append([error,on_hold,ready,in_process, len(data['value'])])
    return finallist, numbers

class MyAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MyAppLayout, self).__init__(orientation='vertical', **kwargs)

        # Button at the top
        self.button = Button(text='Wyślij zapytanie', size_hint_y=None, height=120)
        self.add_widget(self.button)
        self.button.bind(on_press=self.on_button_click)

        # ScrollView for the TextInputs
        self.scroll_view = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height - self.button.height))
        self.inputs_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.inputs_layout.bind(minimum_height=self.inputs_layout.setter('height'))
        self.scroll_view.add_widget(self.inputs_layout)
        self.add_widget(self.scroll_view)

    def on_button_click(self, instance):
        self.inputs_layout.clear_widgets()  # Clear existing TextInputs

        # Fetch data and create a new TextInput for each item
        data, numbers = get_data()
        print(data)
        #print(len(data))
        
        #data = [ ["is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unk", "is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unk", "is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unk123"] ]
        total_height = 0  # Initialize total height for all TextInputs
        if data:
            for item in data:
                text_content = f"Nazwa: {item[0]}\nOpis: {item[1]}\nBłąd: {item[2]}"
                new_text_input = TextInput(text=text_content, readonly=True, halign="left", size_hint_y=None, height=200, multiline=True)
                self.inputs_layout.add_widget(new_text_input)
                total_height += new_text_input.height
        else:
            text_content = "Brak błędów - możesz zjeść ciastko"
            print("elo")
            new_text_input = TextInput(text=text_content, readonly=True, halign="left", size_hint_y=None, height=200)
            self.inputs_layout.add_widget(new_text_input)
            total_height += new_text_input.height
            
        text_content = f"""Liczba kolejek: {numbers[0][4]}\nLiczba błędów: {numbers[0][0]}\nW trakcie: {numbers[0][3]}\nGotowe: {numbers[0][2]}\nWstrzymane: {numbers[0][1]}"""
        new_text_input = TextInput(text=text_content, readonly=True, halign="left", size_hint_y=None, height=200, multiline=True)

        # Update the height of the inputs_layout to accommodate all child widgets
        self.inputs_layout.height = total_height + 200
        self.inputs_layout.add_widget(new_text_input)
        #total_height += new_text_input.height
class TestApp(App):
    def build(self):
        return MyAppLayout()

if __name__ == '__main__':
    TestApp().run()
