from tkinter import *
from scenes.singeplayer import singleplayer
from scenes.multiplayer import multiplayer
from Utils.db import get_money
from variables import frame_colour, button_colour, font, main_background, fall_back_colour


class main_game:
    def __init__(self, window, username, protecting):
        self._window = window
        self._username = username
        self._elements = {}
        self._background = None
        self._balance = 0
        self._gamemode = None
        self._protecting = protecting

    def load_utils(self):
        self._gamemode_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        self._gamemode_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1600, height=500)
        self._elements.update({
            "gamemode_frame": self._gamemode_frame,
        })

        try:
            self._background = PhotoImage(file=main_background)
            bg_label = Label(self._window, image=self._background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
        except Exception as e:
            print(f"Error loading background image: {e}")
            self._window.configure(bg=fall_back_colour)
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username

        try:
            self._balance = get_money(username_value, self._protecting)
        except Exception as e:
            print(f"Error loading balance from DB: {e}")
            self._balance = 0

        self._elements['back_button'] = Button(
            self._window, text="Back", command=self.back_to_main_menu, width=10,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff'
        )
        
        self._elements['play_button'] = Button(
            self._gamemode_frame, text=f"Play (Balance: ${self._balance})", width=40,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.start_game
        )
        self._elements["play_label"] = Label(
            self._gamemode_frame, text=f"Play (Balance: ${self._balance})", width=40,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff'
        )
        self._elements["single_player_button"] = Button(
            self._gamemode_frame, text="Singleplayer", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.singleplayer
        )
        self._elements["multi_player_button"] = Button(
            self._gamemode_frame, text="Multiplayer", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.multiplayer
        )
        self._elements["leaderboard_button"] = Button(
            self._gamemode_frame, text="Leaderboard", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.load_leaderboard
        )

    def clear_screen(self):
        for widget in self._window.winfo_children():
            widget.place_forget()
        self._elements.clear()

    def back_to_main_menu(self):
        self.clear_screen()
        from scenes.main_menu import main_menu
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        MainMenu = main_menu(self._window, username_value, self._protecting)
        MainMenu.run()

    def place_elements(self):
        self._elements['back_button'].place(relx=0.05, rely=0.9, anchor="w")
        self._elements['play_label'].place(relx=0.5, rely=0.5, anchor=CENTER)
        self._elements["single_player_button"].place(relx=0.25, rely=0.2, anchor=CENTER)
        self._elements["multi_player_button"].place(relx=0.75, rely=0.2, anchor=CENTER)
        self._elements["leaderboard_button"].place(relx=0.5, rely=0.8, anchor=CENTER)

    def load_leaderboard(self):
        self.clear_screen()
        from scenes.leaderboard import leaderboard
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        LeaderBoard = leaderboard(self._window, username_value, self._protecting)
        LeaderBoard.run()

    def singleplayer(self):
        if self._gamemode != "singleplayer":
            self._gamemode = "singleplayer"
            self._elements["play_label"].place_forget()
            self._elements["play_button"].place(relx=0.5, rely=0.5, anchor=CENTER)
            self._elements["single_player_button"].config(bg='#404040', activebackground='#404040')
            self._elements["multi_player_button"].config(bg=button_colour, activebackground=button_colour)

    def multiplayer(self):
        if self._gamemode != "multiplayer":
            self._gamemode = "multiplayer"
            self._elements["play_label"].place_forget()
            self._elements["play_button"].place(relx=0.5, rely=0.5, anchor=CENTER)
            self._elements["multi_player_button"].config(bg='#404040', activebackground='#404040')
            self._elements["single_player_button"].config(bg=button_colour, activebackground=button_colour)

    def start_game(self):
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        if self._gamemode == "singleplayer":
            self.clear_screen()
            game = singleplayer(self._window, username_value, self._balance, self._protecting)
            game.run()
        elif self._gamemode == "multiplayer":
            self.clear_screen()
            game = multiplayer(self._window, username_value, self._balance, self._protecting)
            game.run()
        else:
            print("Error: Not starting game")

    def run(self):
        self.clear_screen()
        self.load_utils()
        self.place_elements()
