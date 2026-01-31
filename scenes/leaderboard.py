from tkinter import *
import sqlite3
from variables import *


def comma_number(balance):
    return "{:,}".format(balance)


class leaderboard:
    def __init__(self, window, username):
        self.window = window
        self.username = username
        self.elements = {}
        self.background = None
        self.frame_colour = frame_colour
        self.button_colour = button_colour
        self.font = font
        self.db_path = database_path  # Your DB path

    def load_utils(self):
        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.elements["background_label"] = bg_label
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg='#1803A5')

        # Main container frame
        frame = Frame(self.window, bg=self.frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.1, anchor="n", width=1000, height=900)

        # Create a canvas and scrollbar inside the frame
        canvas = Canvas(frame, bg=self.frame_colour, highlightthickness=0)
        scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # This frame will hold the leaderboard rows
        scrollable_frame = Frame(canvas, bg=self.frame_colour)

        # Put the scrollable_frame inside the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        # Pack canvas and scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Make sure the scrollregion updates when the scrollable_frame size changes
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_configure)

        back_button = Button(
            self.window, text="Back", font=(self.font, 30, 'bold'), width=9,
            relief=RAISED, bd=10, bg=self.button_colour, activebackground=self.button_colour,
            fg='#ffffff', activeforeground='#ffffff',
            command=self.back_to_main_menu
        )

        self.elements = {
            "frame": frame,
            "canvas": canvas,
            "scrollbar": scrollbar,
            "scrollable_frame": scrollable_frame,
            "back_button": back_button,
        }

    def create_leaderboard_screen(self):
        self.elements["back_button"].place(relx=0.1, rely=0.9, anchor=CENTER)
        sf = self.elements["scrollable_frame"]

        # Clear any previous rows
        for widget in sf.winfo_children():
            widget.destroy()

        # Configure grid columns to expand evenly
        sf.grid_columnconfigure(0, weight=1)
        sf.grid_columnconfigure(1, weight=1)
        sf.grid_columnconfigure(2, weight=1)

        # Connect to your database and fetch sorted leaderboard data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, GamesPlayed, Money FROM Users ORDER BY GamesPlayed DESC")
        rows = cursor.fetchall()
        conn.close()

        # Headers
        header_font = (self.font, 15, 'bold')
        Label(sf, text="Username", font=(header_font, 20, 'bold'), bg=self.frame_colour, fg='white', width=15,
              anchor='w') \
            .grid(row=0, column=0, padx=10, pady=5, sticky='w')
        Label(sf, text="Games Played", font=(header_font, 20, 'bold'), bg=self.frame_colour, fg='white', width=15,
              anchor='center') \
            .grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        Label(sf, text="Balance", font=(header_font, 20, 'bold'), bg=self.frame_colour, fg='white', width=20,
              anchor='e') \
            .grid(row=0, column=2, padx=10, pady=5, sticky='e')

        row_bg_colors = ['#757575', '#ABABAB']

        for i, (username, games_played, balance) in enumerate(rows, start=1):
            balance = comma_number(balance)
            bg_color = row_bg_colors[i % 2]

            if username.strip().lower() == self.username.get().strip().lower():
                bg_color = '#FFD700'  # Gold highlight

            Label(sf, text=username, font=(self.font, 16), bg=bg_color,
                  fg='black' if bg_color == '#FFD700' else 'white',
                  width=15, anchor='w').grid(row=i, column=0, padx=10, pady=2, sticky='w')
            Label(sf, text=str(games_played), font=(self.font, 16), bg=bg_color,
                  fg='black' if bg_color == '#FFD700' else 'white',
                  width=10, anchor='center').grid(row=i, column=1, padx=10, pady=2, sticky='ew')
            Label(sf, text=f"${balance}", font=(self.font, 16), bg=bg_color,
                  fg='black' if bg_color == '#FFD700' else 'white',
                  width=18, anchor='e').grid(row=i, column=2, padx=10, pady=2, sticky='e')

    def clear_screen(self):
        for element in self.elements.values():
            element.place_forget()
        self.elements.clear()

    def back_to_main_menu(self):
        self.clear_screen()
        from scenes.main_game import main_game
        MainGame = main_game(self.window, self.username)
        MainGame.run()

    def run(self):
        self.load_utils()
        self.create_leaderboard_screen()
