import random
from tkinter import *
from scenes.quit_menu import quit_menu
from scenes.credits import credits_scene
from scenes.settings import settings_scene
from scenes.main_game import main_game
from Utils.db import get_is_admin
from variables import quotes_path, font, button_colour, frame_colour, main_background, fall_back_colour


def get_random_quote():
    with open(quotes_path) as f:
        lines = f.readlines()
    return random.choice(lines).strip()


class main_menu:
    def __init__(self, window, username, protecting):
        self._window = window
        self._username = username
        self._elements = {}
        self._main_background = None
        self._protecting = protecting

    def clear_main_menu(self):
        for element in self._elements.values():
            element.place_forget()
        self._elements.clear()

    def load_utils(self):
        try:
            self._main_background = PhotoImage(file=main_background)
            bg = Label(self._window, image=self._main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self._elements["background"] = bg
        except Exception as e:
            print(f"Error loading background: {e}")
            self._window.configure(bg=fall_back_colour)

        buttons_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        buttons_frame.place(relx=0.025, rely=0.05, anchor='nw', width=500, height=1000)
        other_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        other_frame.place(relx=0.3, rely=0.165, anchor="w", width=1300, height=250)
        self._elements["buttons_frame"] = buttons_frame
        self._elements["other_frame"] = other_frame

        self._elements["settings_button"] = Button(buttons_frame, text="Settings", width=9, font=(font, 40, 'bold'),
                                                  relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                  activebackground=button_colour, activeforeground='white',
                                                  command=self.load_setting_scene)
        self._elements["quit_button"] = Button(buttons_frame, text="Quit", width=9, font=(font, 40, 'bold'),
                                              relief=RAISED, bd=10, bg=button_colour, fg='white',
                                              activebackground=button_colour, activeforeground='white',
                                              command=self.load_quit_menu)
        self._elements["play_button"] = Button(buttons_frame, text="Play", width=7, font=(font, 70, 'bold'),
                                              relief=RAISED, bd=10, bg=button_colour, fg='white',
                                              activebackground=button_colour, activeforeground='white',
                                              command=self.load_game)
        self._elements["credits_button"] = Button(buttons_frame, text="Credits", width=9, font=(font, 40, 'bold'),
                                                 relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                 activebackground=button_colour, activeforeground='white',
                                                 command=self.load_credits_scene)
        self._elements["log_out_button"] = Button(buttons_frame, text="Log Out", width=9, font=(font, 40, 'bold'),
                                                 relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                 activebackground=button_colour, activeforeground='white',
                                                 command=self.log_out)

        quote = get_random_quote()
        self._elements["quotes_label"] = Label(other_frame, text=quote, font=(font, 20, 'bold'),
                              relief=RAISED, bd=10, bg=button_colour, fg='white', wraplength=1200)

        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        self._elements["logged_in_user"] = Label(other_frame, text=f"Welcome, {username_value}",
                            font=(font, 20, 'bold'), relief=RAISED, bd=10,
                            bg=button_colour, fg='white')

        if get_is_admin(username_value, self._protecting):
            self._elements["admin_button"] = Button(self._window, text="Admin", width=9, font=(font, 40, 'bold'),
                                                   relief=RAISED, bd=10, bg=button_colour, fg='white',
                                                   activebackground=button_colour, activeforeground='white',
                                                   command=self.load_admin_panel)

    def create_main_menu(self):
        self._elements["play_button"].place(relx=0.1, rely=0.05)
        self._elements["settings_button"].place(relx=0.1, rely=0.3)
        self._elements["credits_button"].place(relx=0.1, rely=0.45)
        self._elements["log_out_button"].place(relx=0.1, rely=0.6)
        self._elements["quit_button"].place(relx=0.1, rely=0.85)

        self._elements["quotes_label"].place(relx=0.025, rely=0.4)
        self._elements["logged_in_user"].place(relx=0.025, rely=0.1)

        if "admin_button" in self._elements:
            self._elements["admin_button"].place(relx=0.9, rely=0.9, anchor=CENTER)

        for element in self._elements.values():
            element.lift()

    def log_out(self):
        self.clear_main_menu()
        from scenes.login_scene import login
        login_scene = login(self._window, self._protecting)
        login_scene.run_from_main_menu()

    def load_setting_scene(self):
        self.clear_main_menu()
        setting_scene = settings_scene(self._window, self._username, self._protecting)
        setting_scene.run()

    def load_game(self):
        self.clear_main_menu()
        game_scene = main_game(self._window, self._username, self._protecting)
        game_scene.run()

    def load_quit_menu(self):
        self.clear_main_menu()
        quit_scene = quit_menu(self._window, self._username, self._protecting)
        quit_scene.run()

    def load_credits_scene(self):
        self.clear_main_menu()
        credits = credits_scene(self._window, self._username, self._protecting)
        credits.run()

    def load_admin_panel(self):
        self.clear_main_menu()
        from scenes.admin_panel import admin_panel
        panel = admin_panel(self._window, self._username, self._protecting)
        panel.run()

    def run(self):
        self.load_utils()
        self.create_main_menu()