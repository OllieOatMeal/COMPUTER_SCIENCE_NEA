"""

# Code to load the admin panel to users that have the admin privledge

"""

"""
# Import nessicary functions/ procedures
"""
from tkinter import *
from tkinter import ttk
from variables import font, button_colour, frame_colour, main_background, fall_back_colour
from Utils.db import get_all_usernames, get_user_data, update_user_password, update_user_balance, set_is_admin

"""
# Main class to control the scene
"""
class admin_panel:
    # Initialises the class with parameters passed in and set the base class specific variables 
    def __init__(self, window, username, protecting):
        self._window = window
        self._username = username
        self._protecting = protecting
        self._elements = {}
        self._main_background = None
        self._selected_user = None
        
        self._selected_username = StringVar()
        self._password_var = StringVar()
        self._balance_var = StringVar()
        self._games_var = StringVar()
        self._admin_var = IntVar()

    # Removes all elements from the screen apart from the main background
    def clear_screen(self):
        for element in self._elements.values():
            try:
                element.destroy()
            except:
                try:
                    element.place_forget()
                except:
                    pass
        self._elements.clear()

    # Removes all elements from the screen apart from the main background

    def load_utils(self):
        try:
            self._main_background = PhotoImage(file=main_background)
            bg_label = Label(self._window, image=self._main_background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
            self._elements["background_label"] = bg_label
        except Exception as e:
            print(f"Error loading background image: {e}")
            self._window.configure(bg=fall_back_colour)

        admin_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        admin_frame.place(relx=0.5, rely=0.1, anchor='n', width=1600, height=900)
        self._elements["admin_frame"] = admin_frame

        title_label = Label(admin_frame, text="Admin Control Panel", font=(font, 30, 'bold'),
                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', padx=20)
        title_label.place(relx=0.5, rely=0.03, anchor='n')
        self._elements["title_label"] = title_label

        subtitle_label = Label(admin_frame, text="Manage user accounts and permissions",
                      font=(font, 14, 'bold'), bg=button_colour, fg='#ffffff')
        subtitle_label.place(relx=0.5, rely=0.12, anchor='n')
        self._elements["subtitle_label"] = subtitle_label

        user_label = Label(admin_frame, text="Select User:", font=(font, 18, 'bold'),
                  bg=frame_colour, fg='#ffffff')
        user_label.place(relx=0.12, rely=0.22, anchor='w')
        self._elements["user_label"] = user_label

        usernames = get_all_usernames(self._protecting)
        if not usernames:
            usernames = ["No users found"]

        user_dropdown = ttk.Combobox(admin_frame, textvariable=self._selected_username,
                        values=usernames, state='readonly', font=('Candara', 20))
        user_dropdown.place(relx=0.35, rely=0.22, anchor='w', width=500)
        user_dropdown.bind('<<ComboboxSelected>>', self.on_user_selected)
        self._elements["user_dropdown"] = user_dropdown

        password_label = Label(admin_frame, text="Password:", font=(font, 18),
                      bg=frame_colour, fg='#ffffff')
        password_label.place(relx=0.12, rely=0.34, anchor='w')
        self._elements["password_label"] = password_label

        password_entry = Entry(admin_frame, textvariable=self._password_var, width=32,
                      bg='#ffffff', fg='#000000', relief=SOLID,
                      font=('Candara', 15), bd=2)
        password_entry.place(relx=0.35, rely=0.34, anchor='w')
        self._elements["password_entry"] = password_entry

        balance_label = Label(admin_frame, text="Balance ($):", font=(font, 18),
                    bg=frame_colour, fg='#ffffff')
        balance_label.place(relx=0.12, rely=0.44, anchor='w')
        self._elements["balance_label"] = balance_label

        balance_entry = Entry(admin_frame, textvariable=self._balance_var, width=32,
                     bg='#ffffff', fg='#000000', relief=SOLID,
                     font=('Candara', 15), bd=2)
        balance_entry.place(relx=0.35, rely=0.44, anchor='w')
        self._elements["balance_entry"] = balance_entry

        games_label = Label(admin_frame, text="Games Played:", font=(font, 18),
                   bg=frame_colour, fg='#ffffff')
        games_label.place(relx=0.12, rely=0.54, anchor='w')
        self._elements["games_label"] = games_label

        games_entry = Entry(admin_frame, textvariable=self._games_var, width=32,
                   bg='#ffffff', fg='#000000', relief=SOLID,
                   font=('Candara', 15), bd=2)
        games_entry.place(relx=0.35, rely=0.54, anchor='w')
        self._elements["games_entry"] = games_entry

        admin_check = Checkbutton(admin_frame, text="Administrator Privileges", variable=self._admin_var,
                     font=(font, 18, 'bold'), bg=frame_colour, fg='#ffffff',
                     selectcolor=button_colour, activebackground=frame_colour,
                     activeforeground='#ffffff')
        admin_check.place(relx=0.12, rely=0.64, anchor='w')
        self._elements["admin_check"] = admin_check

        message_label = Label(admin_frame, text="", font=(font, 16, 'bold'),
                    fg='#ffffff', bg=frame_colour, wraplength=800)
        message_label.place(relx=0.5, rely=0.72, anchor=CENTER)
        self._elements["message_label"] = message_label

        button_frame = Frame(admin_frame, bg=frame_colour)
        button_frame.place(relx=0.5, rely=0.86, anchor=CENTER)
        self._elements["button_frame"] = button_frame

        update_button = Button(button_frame, text="Save Changes", font=(font, 22, 'bold'),
                      relief=RAISED, bd=10, bg=button_colour, width=14,
                      activebackground=button_colour, fg='#ffffff',
                      activeforeground='#ffffff', command=self.update_user)
        update_button.pack(side=LEFT, padx=10)
        self._elements["update_button"] = update_button

        clear_button = Button(button_frame, text="Clear Form", font=(font, 22, 'bold'),
                     relief=RAISED, bd=10, bg=button_colour, width=14,
                     activebackground=button_colour, fg='#ffffff',
                     activeforeground='#ffffff', command=self.clear_form)
        clear_button.pack(side=LEFT, padx=10)
        self._elements["clear_button"] = clear_button

        view_db_button = Button(admin_frame, text="View Database", font=(font, 18, 'bold'),
                       relief=RAISED, bd=8, bg=button_colour,
                       activebackground=button_colour, fg='#ffffff',
                       activeforeground='#ffffff', command=self.view_database)
        view_db_button.place(relx=0.93, rely=0.045, anchor='ne')
        self._elements["view_db_button"] = view_db_button

        back_button = Button(self._window, text="Back", font=(font, 22, 'bold'),
                   relief=RAISED, bd=6, bg=button_colour,
                   activebackground=button_colour, fg='#ffffff',
                   activeforeground='#ffffff', command=self.back_to_main_menu, width=8)
        back_button.place(relx=0.025, rely=0.96, anchor='w')
        self._elements["back_button"] = back_button

    # Fills elements on screen with the current selected user's decrypted data
    def on_user_selected(self, event):
        username = self._selected_username.get()
        if not username or username == "No users found":
            return

        user_data = get_user_data(username, self._protecting)
        if user_data:
            self._password_var.set(user_data.get("password", ""))
            self._balance_var.set(str(user_data.get("money", 0)))
            self._games_var.set(str(user_data.get("games_played", 0)))
            self._admin_var.set(1 if user_data.get("is_admin", False) else 0)
            self._elements["message_label"].config(text=f"✓ Loaded data for {username}", fg="#ffffff")

    # Encrypts and updates the database for the selected user
    def update_user(self):
        username = self._selected_username.get()
        if not username or username == "No users found":
            self._elements["message_label"].config(text="⚠ Please select a user first", fg='#ff6600')
            return

        password = self._password_var.get()
        balance_str = self._balance_var.get()
        games_str = self._games_var.get()
        is_admin = self._admin_var.get() == 1

        try:
            balance = int(balance_str) if balance_str else 0
        except ValueError:
            self._elements["message_label"].config(text="⚠ Balance must be a valid number", fg='#ff0000')
            return

        try:
            games = int(games_str) if games_str else 0
        except ValueError:
            self._elements["message_label"].config(text="⚠ Games Played must be a valid number", fg='#ff0000')
            return

        from Utils.db import update_user_password, update_user_balance, set_is_admin, update_money_and_games
        success = True
        if password:
            success = success and update_user_password(username, password, self._protecting)
        success = success and update_money_and_games(username, balance, games, self._protecting)
        success = success and set_is_admin(username, is_admin, self._protecting)

        if success:
            self._elements["message_label"].config(text=f"✓ Successfully updated {username}", fg='#00ff00')
        else:
            self._elements["message_label"].config(text="✗ Update failed - please try again", fg='#ff0000')

    # Removes any data that is in the elements
    def clear_form(self):
        self._selected_username.set("")
        self._password_var.set("")
        self._balance_var.set("")
        self._games_var.set("")
        self._admin_var.set(0)
        self._elements["message_label"].config(text="Form cleared", fg='#aaaaaa')

    # Loads the main menu scene
    def back_to_main_menu(self):
        self.clear_screen()
        from scenes.main_menu import main_menu
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        MainMenu = main_menu(self._window, username_value, self._protecting)
        MainMenu.run()

    # Loads the database viewing scene
    def view_database(self):
        self.clear_screen()
        from scenes.database_viewer import database_viewer
        viewer = database_viewer(self._window, self._username, self._protecting)
        viewer.run()
    # Runs the file (Called remotely)
    def run(self):
        self.load_utils()
