import smtplib
import threading
from email.message import EmailMessage
import ssl
import string
import random

import mysql.connector
from kivy.properties import ObjectProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.material_resources import dp
from kivymd.uix.button import MDFillRoundFlatButton, MDRoundFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.factory import Factory


class RunningPopup(Popup):
    fpop = None

    def set_pop(self, pwin):
        self.fpop = pwin

    def close(self):
        self.fpop.dismiss()


class Start(Screen):
    pop_up = ObjectProperty()

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.text = ''

    def authenticate(self, uid, password):
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select * from admin_info ')
        check = 0
        uid = uid.strip()
        password = password.strip()
        for x in cursor:
            if uid == x[1]:
                if password == x[2]:
                    check = 1

        if check != 1:
            layout = BoxLayout(orientation="vertical")
            label = Label(text='Invalid Credentials', font_size=25)
            button = MDFillRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(50, 25), pos_hint={"x": 0.375})
            layout.add_widget(label)
            layout.add_widget(button)
            popup = Popup(title="LOGIN FAILED !!!", content=layout, size_hint=(None, None), size=(300, 250))
            popup.open()
            button.bind(on_release=popup.dismiss)

        else:
            print("Welcome")
            self.ids.username.text = ''
            self.ids.password.text = ''
            self.manager.current = 'first'
            self.manager.transition.direction = 'left'

    def loading(self):
        layout = BoxLayout(orientation="vertical")
        label = Label(text="Email consisting of your username and password will be sent to your id !!", font_size=18)
        button = MDRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(50, 25), pos_hint={"x": 0.45})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Email Sent", content=layout, size_hint=(None, None), size=(650, 250))
        button.bind(on_release=popup.dismiss)
        popup.open()

        self.pop_up = RunningPopup()
        self.pop_up.open()

        mythread = threading.Thread(target=self.forgot_pswd)
        mythread.start()

    def forgot_pswd(self):
        print("HELLO")
        sender = 'gauravraj6767@gmail.com'
        pswd = 'hatwrllmqwwjcxov'

        receiver = 'joshilraj017182@gmail.com'
        sub = 'Credentials'
        body = """
        Username : {}
        Password : {}
        Do not share with anyone !
        """.format('abc', '123456')

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = sub
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, pswd)
            smtp.sendmail(sender, receiver, em.as_string())

        print("Done")
        self.pop_up.dismiss()


class First(Screen):
    platform_list = []

    def __init__(self, **kwargs):
        super(First, self).__init__(**kwargs)
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select platform from details')
        for i in cursor:
            self.platform_list.append(
                {
                    "text": f"{i[0]}",
                    "viewclass": "OneLineListItem",
                    "icon": "git",
                    "height": dp(56),
                    "on_release": lambda x=f"{i[0]}": self.set_item(x),
                }
            )

        self.menu = MDDropdownMenu(
            caller=self.ids.field,
            items=self.platform_list,
            position="bottom",
            width_mult=4,
        )

    def refresh(self):
        self.platform_list = []
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select platform from details')
        for i in cursor:
            self.platform_list.append(
                {
                    "text": f"{i[0]}",
                    "viewclass": "OneLineListItem",
                    "icon": "git",
                    "height": dp(56),
                    "on_release": lambda x=f"{i[0]}": self.set_item(x),
                }
            )

        self.menu = MDDropdownMenu(
            caller=self.ids.field,
            items=self.platform_list,
            position="bottom",
            width_mult=4,
        )

    def set_item(self, text__item):
        self.ids.field.text = text__item
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute(f'select username, password from details where platform = "{text__item}"')
        for i in cursor:
            self.ids.username.text = i[0]
            self.ids.password.text = i[1]
        self.menu.dismiss()

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.field.text = 'Click to Select Platform Name !!'


class CreateScreen(Screen):

    def generate_random_password(self):
        length = 15
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=length))
        self.ids.password.text = ran

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.platform.text = ''

    def create_record(self, platform, username, password):
        if platform == '' or username == '' or password == '':
            print("Empty Fields Not Accepted !!")
            layout = BoxLayout(orientation="vertical")
            label = Label(text='Empty Fields Not Accepted !!', font_size=25)
            button = MDFillRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.4})
            layout.add_widget(label)
            layout.add_widget(button)
            popup = Popup(title="Empty", content=layout, size_hint=(None, None), size=(400, 250))
            popup.open()
            button.bind(on_release=popup.dismiss)

        else:
            print("Create Page")
            platform = platform.upper()

            db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
            cursor = db_obj.cursor()
            cursor.execute('select max(s_no) from details')
            n = 0
            for i in cursor:
                n = int(i[0])
            n += 1
            cursor.execute('insert into details values({},"{}", "{}", "{}")'.format(n, platform, username, password))
            db_obj.commit()
            self.confirmation(platform)

    def confirmation(self, platform):

        layout = BoxLayout(orientation="vertical")
        label = Label(text='Credentials of {} Stored'.format(platform), font_size=25)
        button = MDFillRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.4})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Success", content=layout, size_hint=(None, None), size=(400, 250))
        popup.open()
        button.bind(on_release=popup.dismiss)


class MainApp(MDApp):
    def build(self):
        Builder.load_file("testing.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        sm = Factory.ScreenManager()
        sm.add_widget(Start())
        sm.add_widget(CreateScreen())
        sm.add_widget(First())

        return sm


MainApp().run()

