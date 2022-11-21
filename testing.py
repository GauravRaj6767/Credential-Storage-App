import os
import sqlite3

os.environ['KIVY_IMAGE'] = 'pil'
import smtplib
import threading
from email.message import EmailMessage
import ssl
import string
import random

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

    def close(self):
        self.fpop.dismiss()


class Start(Screen):
    pop_up = ObjectProperty()

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.text = ''

    def authenticate(self, uid, password):
        MainApp.cur.execute('''CREATE TABLE IF NOT EXISTS admin_info
                                   (S_NO INTEGER PRIMARY KEY, USERNAME TEXT, PASSWORD TEXT,EMAIL TEXT)''')
        MainApp.cur.execute('''INSERT OR IGNORE INTO admin_info values 
                                    (1, 'abc', '123', 'gauravraj6767@gmail.com')''')
        MainApp.con.commit()

        check = 0
        uid = uid.strip()
        password = password.strip()
        res = MainApp.cur.execute('''select * from admin_info''')
        for x in res:
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
        label = Label(text="Email consisting of your\n\nUsername and Password\n\nwill be sent to your id !!", font_size=18)
        button = MDRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(50, 25), pos_hint={'x': 0.35})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Email Sent", content=layout, size_hint=(None, None), size=(350, 250))
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

        MainApp.cur.execute('''CREATE TABLE IF NOT EXISTS details
                                                   (S_NO INTEGER PRIMARY KEY, PLATFORM TEXT, USERNAME TEXT,PASSWORD TEXT)''')
        MainApp.cur.execute('''INSERT OR IGNORE INTO details values 
                                                    (1, 'AMAZON', 'raj123', 'amaze_123456')''')
        MainApp.cur.execute('''INSERT OR IGNORE INTO details values 
                                                    (2, 'FLIPKART', 'flip123', 'abcd123***')''')
        MainApp.cur.execute('''INSERT OR IGNORE INTO details values 
                                                    (3, 'HOTSTAR', 'test456', 'asjkdh***')''')
        MainApp.con.commit()
        MainApp.cur.execute('select platform from details')

        for i in MainApp.cur:
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

        MainApp.cur.execute('''select platform from details''')
        for i in MainApp.cur:
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

        MainApp.cur.execute(f'select username, password from details where platform = "{text__item}"')
        for i in MainApp.cur:
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

            MainApp.cur.execute('select max(s_no) from details')
            n = 0
            for i in MainApp.cur:
                n = int(i[0])
            n += 1
            MainApp.cur.execute('insert into details values({},"{}", "{}", "{}")'.format(n, platform, username, password))
            MainApp.con.commit()
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


class EditScreen(Screen):
    platform_list = []

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)

        MainApp.cur.execute('select platform from details')
        for i in MainApp.cur:
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

        MainApp.cur.execute('select platform from details')
        for i in MainApp.cur:
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

        MainApp.cur.execute(f'select username, password from details where platform = "{text__item}"')
        for i in MainApp.cur:
            self.ids.username.text = i[0]
            self.ids.password.text = i[1]
        self.menu.dismiss()

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.field.text = 'Click to Select Platform Name !!'

    def save(self):
        platform = self.ids.field.text
        uname = self.ids.username.text
        pword = self.ids.password.text

        MainApp.cur.execute(f'update details set username = "{uname}",password = "{pword}" where platform = "{platform}";')
        MainApp.con.commit()
        self.confirmation(platform)

    def confirmation(self, platform):
        layout = BoxLayout(orientation="vertical")
        label = Label(text='Credentials of {} changed !'.format(platform), font_size=25)
        button = MDFillRoundFlatButton(text='OK', font_size=20, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.4})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Success", content=layout, size_hint=(None, None), size=(400, 250))
        popup.open()
        button.bind(on_release=popup.dismiss)


class MainApp(MDApp):
    con = sqlite3.connect('test.db')
    cur = con.cursor()

    def build(self):
        Builder.load_file("testing.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        sm = Factory.ScreenManager()
        sm.add_widget(Start())
        sm.add_widget(First())
        sm.add_widget(CreateScreen())
        sm.add_widget(EditScreen())

        return sm


MainApp().run()

