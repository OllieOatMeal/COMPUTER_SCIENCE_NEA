import random
from scenes.quit_menu import *
from scenes.credits import *
from scenes.settings import *
from scenes.main_game import *

def get_random_quote():
    with open(quotes_path) as f:
        lines = f.readlines()
    return random.choice(lines).strip()

class main_menu:
    def __init__(self, window, username):
        self.window = window
        self.username = username
        self.elements = {}
        self.main_background = None

    def clear_main_menu(self):
        for element in self.elements.values():
            element.place_forget()
        self.elements.clear()

    def load_utils(self):
        # Load background
        try:
            self.main_background = PhotoImage(file=main_background)
            bg = Label(self.window, image=self.main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self.elements["background"] = bg
        except Exception as e:
            print(f"Error loading background: {e}")
            self.window.configure(bg="#1803A5")

        # Frames
        buttons_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        buttons_frame.place(relx=0.025, rely=0.05, anchor='nw', width=500, height=1000)
        other_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        other_frame.place(relx=0.3, rely=0.165, anchor="w", width=1300, height=250)
        self.elements["buttons_frame"] = buttons_frame
        self.elements["other_frame"] = other_frame

        # Buttons
        self.elements["settings_button"] = Button(buttons_frame, text="Settings", width=9, font=(font, 40, 'bold'),
                                                  relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                  activebackground=button_colour, activeforeground='white',
                                                  command=self.load_setting_scene)
        self.elements["quit_button"] = Button(buttons_frame, text="Quit", width=9, font=(font, 40, 'bold'),
                                              relief=RAISED, bd=10, bg=button_colour, fg='white',
                                              activebackground=button_colour, activeforeground='white',
                                              command=self.load_quit_menu)
        self.elements["play_button"] = Button(buttons_frame, text="Play", width=7, font=(font, 70, 'bold'),
                                              relief=RAISED, bd=10, bg=button_colour, fg='white',
                                              activebackground=button_colour, activeforeground='white',
                                              command=self.load_game)
        self.elements["credits_button"] = Button(buttons_frame, text="Credits", width=9, font=(font, 40, 'bold'),
                                                 relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                 activebackground=button_colour, activeforeground='white',
                                                 command=self.load_credits_scene)
        self.elements["log_out_button"] = Button(buttons_frame, text="Log Out", width=9, font=(font, 40, 'bold'),
                                                 relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                 activebackground=button_colour, activeforeground='white',
                                                 command=self.log_out)

        # Labels
        quote = get_random_quote()
        self.elements["quotes_label"] = Label(other_frame, text=quote, font=(font, 20, 'bold'),
                                              relief=RAISED, bd=10, bg=button_colour, fg='white', wraplength=1200)
        self.elements["logged_in_user"] = Label(other_frame, text=f"Welcome, {self.username.get()}",
                                                font=(font, 20, 'bold'), relief=RAISED, bd=10,
                                                bg=button_colour, fg='white')

    def create_main_menu(self):
        # Place elements in frame
        self.elements["play_button"].place(relx=0.1, rely=0.05)
        self.elements["settings_button"].place(relx=0.1, rely=0.3)
        self.elements["credits_button"].place(relx=0.1, rely=0.45)
        self.elements["log_out_button"].place(relx=0.1, rely=0.6)
        self.elements["quit_button"].place(relx=0.1, rely=0.85)

        self.elements["quotes_label"].place(relx=0.025, rely=0.4)
        self.elements["logged_in_user"].place(relx=0.025, rely=0.1)

        # Raise to top
        for element in self.elements.values():
            element.lift()

    def log_out(self):
        self.clear_main_menu()
        from scenes.login_scene import login
        login_scene = login(self.window)
        login_scene.run()

    def load_setting_scene(self):
        self.clear_main_menu()
        setting_scene = settings_scene(self.window, self.username)
        setting_scene.run()

    def load_game(self):
        self.clear_main_menu()
        game_scene = main_game(self.window, self.username)
        game_scene.run()

    def load_quit_menu(self):
        self.clear_main_menu()
        quit_scene = quit_menu(self.window, self.username)
        quit_scene.run()

    def load_credits_scene(self):
        self.clear_main_menu()
        credits = credits_scene(self.window, self.username)
        credits.run()

    def run(self):
        self.load_utils()
        self.create_main_menu()

    def logout(self):
        self.run()
        self.clear_main_menu()
        from scenes.login_scene import login
        login_scene = login(self.window)
        login_scene.acc_deleted()