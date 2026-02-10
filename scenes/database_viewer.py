"""
Database viewer for admins
Shows all users and all fields in decrypted state
"""

from tkinter import *
from tkinter import ttk
from variables import font, button_colour, frame_colour, main_background, fall_back_colour
from Utils.db import get_leaderboard, get_user_data, get_all_usernames


class database_viewer:
    """Database viewer scene for admins"""

    def __init__(self, window, username, protecting):
        """
        Initialise database viewer
        Args:
            window: Tkinter root window
            username: Current logged-in admin username
            protecting: EncryptionService instance
        """
        # Just keep references for the admin view
        self.window = window
        self.username = username
        self.protecting = protecting
        self.elements = {}
        self.main_background = None

    def clear_screen(self):
        """Remove all UI elements from the database viewer"""
        # Clear widgets so the next scene is clean
        for element in self.elements.values():
            try:
                element.place_forget()
            except:
                pass
        self.elements.clear()

    def load_utils(self):
        """Load and create all UI elements for the database viewer"""
        # Build the scrolling table layout
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

        # CREATE MAIN CONTAINER FRAME
        main_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        main_frame.place(relx=0.5, rely=0.05, anchor="n", width=1800, height=860)

        # CREATE TITLE
        title_label = Label(main_frame, text="Database Viewer", 
               font=(font, 34, 'bold'), relief=RAISED, bd=10,
               bg=button_colour, fg='#ffffff', padx=20)
        title_label.pack(pady=10)

        # USER COUNT
        user_count_label = Label(main_frame, text="Loading...",
                font=(font, 16, 'bold'), bg=button_colour, fg='#ffffff')
        user_count_label.pack(pady=5)

        # CREATE SCROLLABLE CANVAS AND SCROLLBAR
        canvas = Canvas(main_frame, bg=frame_colour, highlightthickness=0)
        scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create frame to hold database rows
        scrollable_frame = Frame(canvas, bg=frame_colour)

        # Add scrollable frame to canvas
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        # Pack canvas and scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Update scroll region when content changes
        def on_configure(event):
            # Keep the scroll region in sync with content size
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # Match inner frame width to canvas width
            canvas.itemconfig(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # CREATE BACK BUTTON
        back_button = Button(self.window, text="Back", font=(font, 22, 'bold'),
                     relief=RAISED, bd=6, bg=button_colour, width=8,
                     activebackground=button_colour, fg='#ffffff',
                     activeforeground='#ffffff', command=self.back_to_admin_panel)

        # CREATE REFRESH BUTTON
        refresh_button = Button(self.window, text="Refresh", font=(font, 22, 'bold'),
                    relief=RAISED, bd=6, bg=button_colour, width=8,
                    activebackground=button_colour, fg='#ffffff',
                    activeforeground='#ffffff', command=self.create_database_view)

        # STORE ALL ELEMENTS
        self.elements = {
            "main_frame": main_frame,
            "canvas": canvas,
            "scrollbar": scrollbar,
            "scrollable_frame": scrollable_frame,
            "back_button": back_button,
            "refresh_button": refresh_button,
            "title_label": title_label,
            "user_count_label": user_count_label,
        }

    def create_database_view(self):
        """Display database with all user data decrypted"""
        # Fill the table with current DB data
        # PLACE BUTTONS
        self.elements["back_button"].place(relx=0.05, rely=0.95, anchor='w')
        self.elements["refresh_button"].place(relx=0.95, rely=0.95, anchor='e')
        sf = self.elements["scrollable_frame"]

        # CLEAR PREVIOUS ROWS
        for widget in sf.winfo_children():
            widget.destroy()

        # GET ALL USERNAMES
        usernames = get_all_usernames(self.protecting)

        # UPDATE USER COUNT
        self.elements["user_count_label"].config(text=f"Total Users: {len(usernames) if usernames else 0}")

        if not usernames:
            no_data_label = Label(sf, text="⚠ No users in database", 
                                 font=(font, 18, 'bold'), bg=frame_colour, fg='#ffaa00')
            no_data_label.pack(pady=20)
            return

        # CONFIGURE GRID COLUMNS WITH PROPER WIDTHS
        sf.grid_columnconfigure(0, minsize=40, weight=1)   # Row number
        sf.grid_columnconfigure(1, minsize=180, weight=2)  # Username
        sf.grid_columnconfigure(2, minsize=160, weight=2)  # Password
        sf.grid_columnconfigure(3, minsize=140, weight=2)  # Balance
        sf.grid_columnconfigure(4, minsize=120, weight=1)  # Games
        sf.grid_columnconfigure(5, minsize=100, weight=1)  # Admin
        sf.grid_columnconfigure(6, minsize=200, weight=2)  # Created
        sf.grid_columnconfigure(7, minsize=200, weight=2)  # Last Login

        # CREATE COLUMN HEADERS WITH BETTER STYLING
        header_font = (font, 15, 'bold')
        header_bg = button_colour
        headers = ["#", "Username", "Password", "Balance ($)", "Games", "Admin", "Created At", "Last Login"]
        for col, header_text in enumerate(headers):
            header = Label(sf, text=header_text, font=header_font, bg=header_bg,
                          fg='#ffffff', relief=RIDGE, bd=2, pady=10)
            header.grid(row=0, column=col, sticky='nsew', padx=1)

        # ALTERNATE ROW COLORS
        row_bg_colors = ['#757575', '#8d8d8d']

        # POPULATE DATABASE ROWS
        for i, username in enumerate(usernames, start=1):
            user_data = get_user_data(username, self.protecting)
            
            if not user_data:
                continue

            bg_color = row_bg_colors[i % 2]

            # HIGHLIGHT CURRENT USER IN GOLD
            current_user = self.username.get() if hasattr(self.username, 'get') else self.username
            if username.strip().lower() == (current_user or "").strip().lower():
                bg_color = '#FFD700'
                fg_color = '#000000'
            else:
                fg_color = '#ffffff'

            cell_font = (font, 14)

            # ROW NUMBER
            Label(sf, text=str(i), font=(font, 13, 'bold'), bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, pady=10).grid(row=i, column=0, sticky='nsew', padx=1)

            # USERNAME
            Label(sf, text=username, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='w', padx=10, pady=10).grid(row=i, column=1, sticky='nsew', padx=1)

            # PASSWORD (truncated)
            password = user_data.get('password', 'N/A')
            password_display = password[:15] + '...' if len(password) > 15 else password
            Label(sf, text=password_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='w', padx=10, pady=10).grid(row=i, column=2, sticky='nsew', padx=1)

            # BALANCE (formatted with commas)
            balance = user_data.get('money', 0)
            balance_display = f"${balance:,}"
            Label(sf, text=balance_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='e', padx=10, pady=10).grid(row=i, column=3, sticky='nsew', padx=1)

            # GAMES PLAYED (formatted with commas)
            games = user_data.get('games_played', 0)
            games_display = f"{games:,}"
            Label(sf, text=games_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='e', padx=10, pady=10).grid(row=i, column=4, sticky='nsew', padx=1)

            # ADMIN STATUS (with icon)
            admin_status = 'YES' if user_data.get('is_admin', False) else 'NO'
            admin_fg = '#00ff00' if user_data.get('is_admin', False) else '#ff0000'
            Label(sf, text=admin_status, font=(font, 13, 'bold'), bg=bg_color, fg=admin_fg,
                relief=RIDGE, bd=1, pady=10).grid(row=i, column=5, sticky='nsew', padx=1)

            # CREATED AT (formatted)
            created = user_data.get('created_at', 'N/A')
            created_display = self._format_timestamp(created)
            Label(sf, text=created_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='center', padx=6, pady=10).grid(row=i, column=6, sticky='nsew', padx=1)

            # LAST LOGIN (formatted)
            last_login = user_data.get('last_login', 'Never')
            last_login_display = self._format_timestamp(last_login) if last_login != 'Never' else 'Never'
            Label(sf, text=last_login_display, font=cell_font, bg=bg_color, fg=fg_color,
                relief=RIDGE, bd=1, anchor='center', padx=6, pady=10).grid(row=i, column=7, sticky='nsew', padx=1)

    def _format_timestamp(self, timestamp):
        """Format ISO timestamp to readable date"""
        # Convert ISO strings to a short, readable format
        if not timestamp or timestamp == 'N/A':
            return 'N/A'
        try:
            # Extract date and time from ISO format
            # e.g., "2026-02-05T14:30:45" -> "Feb 5, 2026 14:30"
            parts = timestamp.split('T')
            if len(parts) == 2:
                date_parts = parts[0].split('-')
                time_parts = parts[1].split(':')[:2]  # hours and minutes only
                
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

    def back_to_admin_panel(self):
        """Return to admin panel"""
        # Jump back to the admin panel scene
        self.clear_screen()
        from scenes.admin_panel import admin_panel
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        panel = admin_panel(self.window, username_value, self.protecting)
        panel.run()

    def run(self):
        """Main entry point for database viewer"""
        # Build and show the database viewer
        self.load_utils()
        self.create_database_view()
