import string
import mysql.connector
import random
import ssl
import smtplib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from email.message import EmailMessage
from kivy.uix.screenmanager import ScreenManager, Screen


class DetailsApp(App):
    pass


class WindowManager(ScreenManager):
    pass


class Start(Screen):
    username = 'abc'
    password = '123'

    def __init__(self, **kwargs):
        super(Start, self).__init__(**kwargs)

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
            button = Button(text='OK', font_size=30, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.375})
            layout.add_widget(label)
            layout.add_widget(button)
            popup = Popup(title="LOGIN FAILED !!!", content=layout, size_hint=(None, None), size=(300, 250))
            popup.open()
            button.bind(on_release=popup.dismiss)

        else:
            print("Welcome")
            self.ids.user.text = ''
            self.ids.pword.text = ''
            self.manager.current = 'first'
            self.manager.transition.direction = 'up'

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
        """.format(self.username, self.password)

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = sub
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, pswd)
            smtp.sendmail(sender, receiver, em.as_string())

        layout = BoxLayout(orientation="vertical")
        label = Label(text="Email consisting of your username and password has been sent to your id !!", font_size=18)
        button = Button(text='OK', font_size=30, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.45})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Email Sent", content=layout, size_hint=(None, None), size=(650, 250))
        popup.open()
        button.bind(on_release=popup.dismiss)

    def clear(self):
        self.ids.user.text = ''
        self.ids.pword.text = ''


class FirstScreen(Screen):
    platform_list = []

    def __init__(self, **kwargs):
        super(FirstScreen, self).__init__(**kwargs)
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select platform from details')
        for i in cursor:
            self.platform_list.append(i[0])

    def display(self, platform):
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select * from details')
        check = 0
        platform = platform.lower()
        u = ''
        p = ''
        for x in cursor:
            if platform == x[1].lower():
                u = x[2]
                p = x[3]
                break

        print("Success")
        self.ids.u.text = u
        self.ids.p.text = p

    def refresh(self):
        self.platform_list = []
        db_obj = mysql.connector.connect(host="localhost", user="root", password="", database='project')
        cursor = db_obj.cursor()
        cursor.execute('select platform from details')
        for i in cursor:
            self.platform_list.append(i[0])

    def clear(self):
        self.ids.u.text = ''
        self.ids.p.text = ''
        self.ids.platform.text = "Select Platform"


class CreateScreen(Screen):

    def __init__(self, **kwargs):
        super(CreateScreen, self).__init__(**kwargs)

    def create(self, platform, username, password):
        print("Create Page")
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

    def check(self, platform, username, password):
        if platform == '' or username == '' or password == '':
            layout = BoxLayout(orientation="vertical")
            label = Label(text="Empty Fields not Accepted !!", font_size=25)
            button = Button(text='OK', font_size=30, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.375})
            layout.add_widget(label)
            layout.add_widget(button)
            popup = Popup(title="Failed To Enter Data !!", content=layout, size_hint=(None, None), size=(400, 250))
            popup.open()
            button.bind(on_release=popup.dismiss)
        else:
            self.manager.current = 'first'
            self.manager.transition.direction = 'right'
            self.create(platform, username, password)

    def confirmation(self, platform):
        layout = BoxLayout(orientation="vertical")
        label = Label(text='Credentials of {} Stored'.format(platform), font_size=25)
        button = Button(text='OK', font_size=30, size_hint=(None, None), size=(75, 50), pos_hint={"x": 0.375})
        layout.add_widget(label)
        layout.add_widget(button)
        popup = Popup(title="Success", content=layout, size_hint=(None, None), size=(500, 250))
        popup.open()
        button.bind(on_release=popup.dismiss)

    def generate_random_password(self):
        length = 15
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=length))
        self.ids.password.text = ran


DetailsApp().run()

