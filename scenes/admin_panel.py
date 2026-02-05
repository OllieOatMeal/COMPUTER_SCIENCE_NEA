"""
Admin panel for managing users
Only accessible to admin accounts
"""

from tkinter import *
from tkinter import ttk
from variables import font, button_colour, frame_colour, main_background, fall_back_colour
from Utils.db import get_all_usernames, get_user_data, update_user_password, update_user_balance, set_is_admin


class admin_panel:
    """Admin panel scene for user management"""

    def __init__(self, window, username, protecting):
        """
        Initialise admin panel
        Args:
            window: Tkinter root window
            username: Current logged-in admin username
            protecting: EncryptionService instance
        """
        self.window = window
        self.username = username
        self.protecting = protecting
        self.elements = {}
        self.main_background = None
        self.selected_user = None
        
        # String variables for form fields
        self.selected_username = StringVar()
        self.password_var = StringVar()
        self.balance_var = StringVar()
        self.games_var = StringVar()
        self.admin_var = IntVar()

    def clear_screen(self):
        """Remove all UI elements from the admin panel"""
        for element in self.elements.values():
            try:
                element.place_forget()
            except:
                pass
        self.elements.clear()

    def load_utils(self):
        """Load and create all UI elements for the admin panel"""
        # LOAD BACKGROUND IMAGE
        try:
            self.main_background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.main_background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
            self.elements["background_label"] = bg_label
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg=fall_back_colour)

        # CREATE MAIN FRAME
        admin_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        admin_frame.place(relx=0.5, rely=0.1, anchor='n', width=1600, height=900)
        self.elements["admin_frame"] = admin_frame

        # TITLE LABEL
        title_label = Label(admin_frame, text="Admin Control Panel", font=(font, 30, 'bold'),
                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', padx=20)
        title_label.place(relx=0.5, rely=0.03, anchor='n')
        self.elements["title_label"] = title_label

        # SUBTITLE
        subtitle_label = Label(admin_frame, text="Manage user accounts and permissions",
                      font=(font, 14, 'bold'), bg=button_colour, fg='#ffffff')
        subtitle_label.place(relx=0.5, rely=0.12, anchor='n')
        self.elements["subtitle_label"] = subtitle_label

        user_label = Label(admin_frame, text="Select User:", font=(font, 18, 'bold'),
                  bg=frame_colour, fg='#ffffff')
        user_label.place(relx=0.12, rely=0.22, anchor='w')
        self.elements["user_label"] = user_label

        # Get all usernames for dropdown
        usernames = get_all_usernames(self.protecting)
        if not usernames:
            usernames = ["No users found"]

        user_dropdown = ttk.Combobox(admin_frame, textvariable=self.selected_username,
                        values=usernames, state='readonly', font=('Candara', 20))
        user_dropdown.place(relx=0.35, rely=0.22, anchor='w', width=500)
        user_dropdown.bind('<<ComboboxSelected>>', self.on_user_selected)
        self.elements["user_dropdown"] = user_dropdown

        # PASSWORD FIELD
        password_label = Label(admin_frame, text="Password:", font=(font, 18),
                      bg=frame_colour, fg='#ffffff')
        password_label.place(relx=0.12, rely=0.34, anchor='w')
        self.elements["password_label"] = password_label

        password_entry = Entry(admin_frame, textvariable=self.password_var, width=32,
                      bg='#ffffff', fg='#000000', relief=SOLID,
                      font=('Candara', 15), bd=2)
        password_entry.place(relx=0.35, rely=0.34, anchor='w')
        self.elements["password_entry"] = password_entry

        # BALANCE FIELD
        balance_label = Label(admin_frame, text="Balance ($):", font=(font, 18),
                    bg=frame_colour, fg='#ffffff')
        balance_label.place(relx=0.12, rely=0.44, anchor='w')
        self.elements["balance_label"] = balance_label

        balance_entry = Entry(admin_frame, textvariable=self.balance_var, width=32,
                     bg='#ffffff', fg='#000000', relief=SOLID,
                     font=('Candara', 15), bd=2)
        balance_entry.place(relx=0.35, rely=0.44, anchor='w')
        self.elements["balance_entry"] = balance_entry

        # GAMES PLAYED FIELD
        games_label = Label(admin_frame, text="Games Played:", font=(font, 18),
                   bg=frame_colour, fg='#ffffff')
        games_label.place(relx=0.12, rely=0.54, anchor='w')
        self.elements["games_label"] = games_label

        games_entry = Entry(admin_frame, textvariable=self.games_var, width=32,
                   bg='#ffffff', fg='#000000', relief=SOLID,
                   font=('Candara', 15), bd=2)
        games_entry.place(relx=0.35, rely=0.54, anchor='w')
        self.elements["games_entry"] = games_entry

        # ADMIN STATUS CHECKBOX
        admin_check = Checkbutton(admin_frame, text="Administrator Privileges", variable=self.admin_var,
                     font=(font, 18, 'bold'), bg=frame_colour, fg='#ffffff',
                     selectcolor=button_colour, activebackground=frame_colour,
                     activeforeground='#ffffff')
        admin_check.place(relx=0.12, rely=0.64, anchor='w')
        self.elements["admin_check"] = admin_check

        # MESSAGE LABEL (for feedback)
        message_label = Label(admin_frame, text="", font=(font, 16, 'bold'),
                    fg='#ffffff', bg=frame_colour, wraplength=800)
        message_label.place(relx=0.5, rely=0.72, anchor=CENTER)
        self.elements["message_label"] = message_label

        # BUTTON FRAME for better layout
        button_frame = Frame(admin_frame, bg=frame_colour)
        button_frame.place(relx=0.5, rely=0.86, anchor=CENTER)
        self.elements["button_frame"] = button_frame

        # UPDATE BUTTON
        update_button = Button(button_frame, text="Save Changes", font=(font, 22, 'bold'),
                      relief=RAISED, bd=10, bg=button_colour, width=14,
                      activebackground=button_colour, fg='#ffffff',
                      activeforeground='#ffffff', command=self.update_user)
        update_button.pack(side=LEFT, padx=10)
        self.elements["update_button"] = update_button

        # CLEAR BUTTON
        clear_button = Button(button_frame, text="Clear Form", font=(font, 22, 'bold'),
                     relief=RAISED, bd=10, bg=button_colour, width=14,
                     activebackground=button_colour, fg='#ffffff',
                     activeforeground='#ffffff', command=self.clear_form)
        clear_button.pack(side=LEFT, padx=10)
        self.elements["clear_button"] = clear_button

        # VIEW DATABASE BUTTON
        view_db_button = Button(admin_frame, text="View Database", font=(font, 18, 'bold'),
                       relief=RAISED, bd=8, bg=button_colour,
                       activebackground=button_colour, fg='#ffffff',
                       activeforeground='#ffffff', command=self.view_database)
        view_db_button.place(relx=0.93, rely=0.045, anchor='ne')
        self.elements["view_db_button"] = view_db_button

        # BACK BUTTON
        back_button = Button(self.window, text="Back", font=(font, 22, 'bold'),
                   relief=RAISED, bd=6, bg=button_colour,
                   activebackground=button_colour, fg='#ffffff',
                   activeforeground='#ffffff', command=self.back_to_main_menu, width=8)
        back_button.place(relx=0.025, rely=0.96, anchor='w')
        self.elements["back_button"] = back_button

    def on_user_selected(self, event):
        """Called when a user is selected from dropdown"""
        username = self.selected_username.get()
        if not username or username == "No users found":
            return

        user_data = get_user_data(username, self.protecting)
        if user_data:
            self.password_var.set(user_data.get("password", ""))
            self.balance_var.set(str(user_data.get("money", 0)))
            self.games_var.set(str(user_data.get("games_played", 0)))
            self.admin_var.set(1 if user_data.get("is_admin", False) else 0)
            self.elements["message_label"].config(text=f"✓ Loaded data for {username}", fg="#ffffff")

    def update_user(self):
        """Update the selected user's data"""
        username = self.selected_username.get()
        if not username or username == "No users found":
            self.elements["message_label"].config(text="⚠ Please select a user first", fg='#ff6600')
            return

        password = self.password_var.get()
        balance_str = self.balance_var.get()
        games_str = self.games_var.get()
        is_admin = self.admin_var.get() == 1

        # Validate balance
        try:
            balance = int(balance_str) if balance_str else 0
        except ValueError:
            self.elements["message_label"].config(text="⚠ Balance must be a valid number", fg='#ff0000')
            return

        # Validate games
        try:
            games = int(games_str) if games_str else 0
        except ValueError:
            self.elements["message_label"].config(text="⚠ Games Played must be a valid number", fg='#ff0000')
            return

        # Update database
        from Utils.db import update_user_password, update_user_balance, set_is_admin, update_money_and_games
        success = True
        if password:
            success = success and update_user_password(username, password, self.protecting)
        success = success and update_money_and_games(username, balance, games, self.protecting)
        success = success and set_is_admin(username, is_admin, self.protecting)

        if success:
            self.elements["message_label"].config(text=f"✓ Successfully updated {username}", fg='#00ff00')
        else:
            self.elements["message_label"].config(text="✗ Update failed - please try again", fg='#ff0000')

    def clear_form(self):
        """Clear all form fields"""
        self.selected_username.set("")
        self.password_var.set("")
        self.balance_var.set("")
        self.games_var.set("")
        self.admin_var.set(0)
        self.elements["message_label"].config(text="Form cleared", fg='#aaaaaa')

    def back_to_main_menu(self):
        """Return to main menu"""
        self.clear_screen()
        from scenes.main_menu import main_menu
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        MainMenu = main_menu(self.window, username_value, self.protecting)
        MainMenu.run()

    def view_database(self):
        """Open the database viewer"""
        self.clear_screen()
        from scenes.database_viewer import database_viewer
        viewer = database_viewer(self.window, self.username, self.protecting)
        viewer.run()

    def run(self):
        """Main entry point for admin panel"""
        self.load_utils()
