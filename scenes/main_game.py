from tkinter import *
from scenes.singeplayer import *
from scenes.multiplayer import *
import sqlite3

class main_game:
    def __init__(self, window, username):
        self.window = window
        self.username = username
        self.elements = {}
        self.background = None
        self.balance = 0
        self.gamemode = None

    def load_utils(self):
        self.gamemode_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        self.gamemode_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1600, height=500)
        self.elements.update({
            "gamemode_frame": self.gamemode_frame,
        })

        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg='#1803A5')  # fallback background color
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Money FROM Users WHERE UserName = (?)", (self.username.get(),))
            result = cursor.fetchone()
            if result:
                self.balance = result[0]
            else:
                self.balance = 0
            conn.close()
        except Exception as e:
            print(f"Error loading balance from DB: {e}")
            self.balance = 0

        self.elements['back_button'] = Button(
            self.window, text="Back", command=self.back_to_main_menu, width=10,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff'
        )
        self.elements['play_button'] = Button(
            self.gamemode_frame, text=f"Play (Balance: ${self.balance})", width=40,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.start_game
        )
        self.elements["play_label"] = Label(
            self.gamemode_frame, text=f"Play (Balance: ${self.balance})", width=40,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff'
        )
        self.elements["single_player_button"] = Button(
            self.gamemode_frame, text="Singleplayer", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.singleplayer
        )
        self.elements["multi_player_button"] = Button(
            self.gamemode_frame, text="Multiplayer", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.multiplayer
        )
        self.elements["leaderboard_button"] = Button(
            self.gamemode_frame, text="Leaderboard", width=12,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff',
            command=self.load_leaderboard
        )

    def clear_screen(self):
        # Remove all widgets from the window
        for widget in self.window.winfo_children():
            widget.place_forget()
        # Clear stored elements
        self.elements.clear()

    def back_to_main_menu(self):
        self.clear_screen()
        from scenes.main_menu import main_menu
        MainMenu = main_menu(self.window, self.username)
        MainMenu.run()

    def place_elements(self):
        self.elements['back_button'].place(relx=0.05, rely=0.9, anchor="w")
        self.elements['play_label'].place(relx=0.5, rely=0.5, anchor=CENTER)
        self.elements["single_player_button"].place(relx=0.25, rely=0.2, anchor=CENTER)
        self.elements["multi_player_button"].place(relx=0.75, rely=0.2, anchor=CENTER)
        self.elements["leaderboard_button"].place(relx=0.5, rely=0.8, anchor=CENTER)

    def load_leaderboard(self):
        self.clear_screen()
        from scenes.leaderboard import leaderboard
        LeaderBoard = leaderboard(self.window, self.username)
        LeaderBoard.run()

    def singleplayer(self):
        if self.gamemode != "singleplayer":
            self.gamemode = "singleplayer"
            self.elements["play_label"].place_forget()
            self.elements["play_button"].place(relx=0.5, rely=0.5, anchor=CENTER)
            self.elements["single_player_button"].config(bg='#404040', activebackground='#404040')
            self.elements["multi_player_button"].config(bg=button_colour, activebackground=button_colour)

    def multiplayer(self):
        if self.gamemode != "multiplayer":
            self.gamemode = "multiplayer"
            self.elements["play_label"].place_forget()
            self.elements["play_button"].place(relx=0.5, rely=0.5, anchor=CENTER)
            self.elements["multi_player_button"].config(bg='#404040', activebackground='#404040')
            self.elements["single_player_button"].config(bg=button_colour, activebackground=button_colour)

    def start_game(self):
        if self.gamemode == "singleplayer":
            self.clear_screen()
            game = singleplayer(self.window, self.username, self.balance)
            game.run()
        elif self.gamemode == "multiplayer":
            self.clear_screen()
            game = multiplayer(self.window, self.username, self.balance)
            game.run()
        else:
            print("Error: Not starting game")

    def run(self):
        self.clear_screen()
        self.load_utils()
        self.place_elements()
