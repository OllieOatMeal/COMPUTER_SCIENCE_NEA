"""

# Code to load the database viewer to users that have the admin privilege

"""

"""
# Import necessary functions/ procedures
"""
from tkinter import *
from tkinter import ttk
from Utils.variables import font, button_colour, frame_colour, main_background, fall_back_colour
from Utils.db import get_leaderboard, get_user_data, get_all_usernames

"""
# Main class to control the scene
"""
class database_viewer:
    # Initialises the class with parameters passed in and set the base class specific variables 
    def __init__(self, window, username, protecting):
        self._window = window
        self._username = username
        self._protecting = protecting
        self._elements = {}
        self._main_background = None

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

    # Load the background for the scene
    # Load any data from external files
    # Create any elements required for the GUI / Scene
    # Place all base elements on screen
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

        main_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        main_frame.place(relx=0.5, rely=0.05, anchor="n", width=1800, height=860)

        title_label = Label(main_frame, text="Database Viewer", 
               font=(font, 34, 'bold'), relief=RAISED, bd=10,
               bg=button_colour, fg='#ffffff', padx=20)
        title_label.pack(pady=10)

        user_count_label = Label(main_frame, text="Loading...",
                font=(font, 16, 'bold'), bg=button_colour, fg='#ffffff')
        user_count_label.pack(pady=5)

        canvas = Canvas(main_frame, bg=frame_colour, highlightthickness=0)
        scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = Frame(canvas, bg=frame_colour)

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        back_button = Button(self._window, text="Back", font=(font, 22, 'bold'),
                     relief=RAISED, bd=6, bg=button_colour, width=8,
                     activebackground=button_colour, fg='#ffffff',
                     activeforeground='#ffffff', command=self.back_to_admin_panel)

        refresh_button = Button(self._window, text="Refresh", font=(font, 22, 'bold'),
                    relief=RAISED, bd=6, bg=button_colour, width=8,
                    activebackground=button_colour, fg='#ffffff',
                    activeforeground='#ffffff', command=self.create_database_view)

        self._elements = {
            "main_frame": main_frame,
            "canvas": canvas,
            "scrollbar": scrollbar,
            "scrollable_frame": scrollable_frame,
            "back_button": back_button,
            "refresh_button": refresh_button,
            "title_label": title_label,
            "user_count_label": user_count_label,
        }

    # Creates and displays the database view with user information in a table format
    def create_database_view(self):
        self._elements["back_button"].place(relx=0.05, rely=0.95, anchor='w')
        self._elements["refresh_button"].place(relx=0.95, rely=0.95, anchor='e')
        sf = self._elements["scrollable_frame"]

        for widget in sf.winfo_children():
            widget.destroy()

        usernames = get_all_usernames(self._protecting)

        self._elements["user_count_label"].config(text=f"Total Users: {len(usernames) if usernames else 0}")

        if not usernames:
            no_data_label = Label(sf, text="⚠ No users in database", 
                                 font=(font, 18, 'bold'), bg=frame_colour, fg='#ffaa00')
            no_data_label.pack(pady=20)
            return

        sf.grid_columnconfigure(0, minsize=40, weight=1)
        sf.grid_columnconfigure(1, minsize=180, weight=2)
        sf.grid_columnconfigure(2, minsize=160, weight=2)
        sf.grid_columnconfigure(3, minsize=140, weight=2)
        sf.grid_columnconfigure(4, minsize=120, weight=1)
        sf.grid_columnconfigure(5, minsize=100, weight=1)
        sf.grid_columnconfigure(6, minsize=200, weight=2)
        sf.grid_columnconfigure(7, minsize=200, weight=2)

        header_font = (font, 15, 'bold')
        header_bg = button_colour
        headers = ["#", "Username", "Password", "Balance ($)", "Games", "Admin", "Created At", "Last Login"]
        for col, header_text in enumerate(headers):
            header = Label(sf, text=header_text, font=header_font, bg=header_bg,
                          fg='#ffffff', relief=RIDGE, bd=2, pady=10)
            header.grid(row=0, column=col, sticky='nsew', padx=1)

        row_bg_colors = ['#757575', '#8d8d8d']

        for i, username in enumerate(usernames, start=1):
            user_data = get_user_data(username, self._protecting)
            
            if not user_data:
                continue

            bg_color = row_bg_colors[i % 2]

            current_user = self._username.get() if hasattr(self._username, 'get') else self._username
            if username.strip().lower() == (current_user or "").strip().lower():
                bg_color = '#FFD700'
                fg_color = '#000000'
            else:
                fg_color = '#ffffff'

            cell_font = (font, 14)

            Label(sf, text=str(i), font=(font, 13, 'bold'), bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, pady=10).grid(row=i, column=0, sticky='nsew', padx=1)

            Label(sf, text=username, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='w', padx=10, pady=10).grid(row=i, column=1, sticky='nsew', padx=1)

            password = user_data.get('password', 'N/A')
            password_display = password[:15] + '...' if len(password) > 15 else password
            Label(sf, text=password_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='w', padx=10, pady=10).grid(row=i, column=2, sticky='nsew', padx=1)

            balance = user_data.get('money', 0)
            balance_display = f"${balance:,}"
            Label(sf, text=balance_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='e', padx=10, pady=10).grid(row=i, column=3, sticky='nsew', padx=1)

            games = user_data.get('games_played', 0)
            games_display = f"{games:,}"
            Label(sf, text=games_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='e', padx=10, pady=10).grid(row=i, column=4, sticky='nsew', padx=1)

            admin_status = 'YES' if user_data.get('is_admin', False) else 'NO'
            admin_fg = '#00ff00' if user_data.get('is_admin', False) else '#ff0000'
            Label(sf, text=admin_status, font=(font, 13, 'bold'), bg=bg_color, fg=admin_fg,
                relief=RIDGE, bd=1, pady=10).grid(row=i, column=5, sticky='nsew', padx=1)

            created = user_data.get('created_at', 'N/A')
            created_display = self._format_timestamp(created)
            Label(sf, text=created_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='center', padx=6, pady=10).grid(row=i, column=6, sticky='nsew', padx=1)

            last_login = user_data.get('last_login', 'Never')
            last_login_display = self._format_timestamp(last_login) if last_login != 'Never' else 'Never'
            Label(sf, text=last_login_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='center', padx=6, pady=10).grid(row=i, column=7, sticky='nsew', padx=1)

    # Formats a timestamp string into a readable date and time format
    def _format_timestamp(self, timestamp):
        if not timestamp or timestamp == 'N/A':
            return 'N/A'
        try:
            parts = timestamp.split('T')
            if len(parts) == 2:
                date_parts = parts[0].split('-')
                time_parts = parts[1].split(':')[:2]
                
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                year = date_parts[0]
                month = months[int(date_parts[1]) - 1]
                day = int(date_parts[2])
                time = ':'.join(time_parts)
                
                return f"{month} {day}, {year} {time}"
        except:
            pass
        return timestamp

    # Loads the admin panel scene
    def back_to_admin_panel(self):
        self.clear_screen()
        from scenes.admin_panel import admin_panel
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        panel = admin_panel(self._window, username_value, self._protecting)
        panel.run()

    # Runs the file (Called remotely)
    def run(self):
        self.load_utils()
        self.create_database_view()
