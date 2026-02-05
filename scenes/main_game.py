"""
Screen to pick which game you want to play - singleplayer or multiplayer
"""

from tkinter import *
from scenes.singeplayer import singleplayer
from scenes.multiplayer import multiplayer
from Utils.db import get_money
from variables import frame_colour, button_colour, font, main_background, fall_back_colour


class main_game:
    """Game mode selection screen"""

    def __init__(self, window, username, protecting):
        """
        Initialise main game scene
        Args:
            window: Tkinter root window
            username: Current logged-in username
            protecting: EncryptionService instance
        """
        self.window = window
        self.username = username
        self.elements = {}
        self.background = None
        self.balance = 0
        self.gamemode = None
        self.protecting = protecting

    def load_utils(self):
        """
        Load and create all UI elements for the game mode selection screen
        Sets up background and game mode frame
        """
        # CREATE GAMEMODE FRAME
        self.gamemode_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        self.gamemode_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1600, height=500)
        self.elements.update({
            "gamemode_frame": self.gamemode_frame,
        })

        # LOAD BACKGROUND IMAGE
        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg=fall_back_colour)  # fallback background color
        # Determine actual username string (supports StringVar or plain str)
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        # QUERY DATABASE FOR PLAYER BALANCE (centralised in Utils.db)
        try:
            self.balance = get_money(username_value, self.protecting)
        except Exception as e:
            print(f"Error loading balance from DB: {e}")
            self.balance = 0

        # CREATE BACK BUTTON
        self.elements['back_button'] = Button(
            self.window, text="Back", command=self.back_to_main_menu, width=10,
            font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff',
            activebackground=button_colour, activeforeground='#ffffff'
        )
        
        # CREATE GAME MODE BUTTONS
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
        """Remove all UI elements from the game screen"""
        for widget in self.window.winfo_children():
            widget.place_forget()
        self.elements.clear()

    def back_to_main_menu(self):
        """Return to main menu"""
        self.clear_screen()
        from scenes.main_menu import main_menu
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        MainMenu = main_menu(self.window, username_value, self.protecting)
        MainMenu.run()

    def place_elements(self):
        """Position all UI elements on the game mode selection screen"""
        self.elements['back_button'].place(relx=0.05, rely=0.9, anchor="w")
        self.elements['play_label'].place(relx=0.5, rely=0.5, anchor=CENTER)
        self.elements["single_player_button"].place(relx=0.25, rely=0.2, anchor=CENTER)
        self.elements["multi_player_button"].place(relx=0.75, rely=0.2, anchor=CENTER)
        self.elements["leaderboard_button"].place(relx=0.5, rely=0.8, anchor=CENTER)

    def load_leaderboard(self):
        """Load and display the leaderboard scene"""
        self.clear_screen()
        from scenes.leaderboard import leaderboard
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        LeaderBoard = leaderboard(self.window, username_value, self.protecting)
        LeaderBoard.run()

    def singleplayer(self):
        """
        Select singleplayer game mode
        Highlights singleplayer button and displays play button
        """
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
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        if self.gamemode == "singleplayer":
            self.clear_screen()
            game = singleplayer(self.window, username_value, self.balance, self.protecting)
            game.run()
        elif self.gamemode == "multiplayer":
            self.clear_screen()
            game = multiplayer(self.window, username_value, self.balance, self.protecting)
            game.run()
        else:
            print("Error: Not starting game")

    def run(self):
        self.clear_screen()
        self.load_utils()
        self.place_elements()
