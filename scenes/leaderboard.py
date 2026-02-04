"""
Shows the leaderboard with all players ranked by games played and money
"""

from tkinter import *
from Utils.db import get_leaderboard
from variables import *


def comma_number(balance):
    """Format a number to show commas in thousands places"""
    return "{:,}".format(balance)


class leaderboard:
    """
    Leaderboard scene controller
    Displays player rankings and game statistics
    """

    def __init__(self, window, username, protecting):
        """
        Initialise leaderboard scene
        Args:
            window: Tkinter root window
            username: Current logged-in username
            protecting: EncryptionService instance
        """
        self.window = window
        self.username = username
        self.elements = {}
        self.background = None
        self.frame_colour = frame_colour
        self.button_colour = button_colour
        self.font = font
        self.db_path = database_path
        self.protecting = protecting

    def load_utils(self):
        """
        Load and create all UI elements for the leaderboard
        Sets up background, scrollable frame, and database query results
        """
        # LOAD BACKGROUND IMAGE
        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.elements["background_label"] = bg_label
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg='#1803A5')

        # CREATE MAIN CONTAINER FRAME
        frame = Frame(self.window, bg=self.frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.1, anchor="n", width=1000, height=900)

        # CREATE SCROLLABLE CANVAS AND SCROLLBAR
        canvas = Canvas(frame, bg=self.frame_colour, highlightthickness=0)
        scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create frame to hold leaderboard rows
        scrollable_frame = Frame(canvas, bg=self.frame_colour)

        # Add scrollable frame to canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        # Pack canvas and scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Update scroll region when content changes
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_configure)

        # CREATE BACK BUTTON
        back_button = Button(
            self.window, text="Back", font=(self.font, 30, 'bold'), width=9,
            relief=RAISED, bd=10, bg=self.button_colour, activebackground=self.button_colour,
            fg='#ffffff', activeforeground='#ffffff',
            command=self.back_to_main_menu
        )

        # STORE ALL ELEMENTS
        self.elements = {
            "frame": frame,
            "canvas": canvas,
            "scrollbar": scrollbar,
            "scrollable_frame": scrollable_frame,
            "back_button": back_button,
        }

    def create_leaderboard_screen(self):
        """
        Display leaderboard with sorted player data
        Queries database and populates scrollable list with rankings
        """
        # PLACE BACK BUTTON
        self.elements["back_button"].place(relx=0.1, rely=0.9, anchor=CENTER)
        sf = self.elements["scrollable_frame"]

        # CLEAR PREVIOUS ROWS
        for widget in sf.winfo_children():
            widget.destroy()

        # CONFIGURE GRID COLUMNS
        sf.grid_columnconfigure(0, weight=1)
        sf.grid_columnconfigure(1, weight=1)
        sf.grid_columnconfigure(2, weight=1)

        # QUERY DATABASE FOR LEADERBOARD DATA (centralised, decrypts usernames)
        rows = get_leaderboard(self.protecting, order_by="GamesPlayed")

        # CREATE COLUMN HEADERS
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

        # ALTERNATE ROW COLOURS FOR READABILITY
        row_bg_colors = ['#757575', '#ABABAB']

        # POPULATE LEADERBOARD ROWS
        for i, (username, games_played, balance) in enumerate(rows, start=1):
            balance = comma_number(balance)
            bg_color = row_bg_colors[i % 2]

            # HIGHLIGHT CURRENT USER IN GOLD
            # Compare against provided username (StringVar or str)
            current_user = self.username.get() if hasattr(self.username, 'get') else self.username
            if username.strip().lower() == (current_user or "").strip().lower():
                bg_color = '#FFD700'

            # CREATE ROW LABELS
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
        """Remove all UI elements from the leaderboard screen"""
        for element in self.elements.values():
            element.place_forget()
        self.elements.clear()

    def back_to_main_menu(self):
        """Return to main game screen"""
        self.clear_screen()
        from scenes.main_game import main_game
        MainGame = main_game(self.window, self.username)
        MainGame.run()

    def run(self):
        self.load_utils()
        self.create_leaderboard_screen()
