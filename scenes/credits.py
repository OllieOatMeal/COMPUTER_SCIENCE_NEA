from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour


class credits_scene:
    def __init__(self, window, username, protecting):
        self.window = window
        self.elements = {}
        self.main_background = None
        self.username = username
        self.protecting = protecting

    def clear_screen(self):
        for element in self.elements.values():
            try:
                element.destroy()
            except:
                try:
                    element.place_forget()
                except:
                    pass
        self.elements.clear()

    def load_utils(self):
        self.credits_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        self.credits_frame.place(relx=0.5, rely=0.1, anchor="n", width=1500, height=700)
        
        try:
            self.main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self.window, bg=fall_back_colour, bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            img_background = Label(self.window, image=self.main_background, bd=0)
            img_background.place(x=0, y=0)
            img_background.lower()

        back_button = Button(self.window, text="Back", width=10, font=(font, 40, 'bold'), relief=RAISED, bd=10, 
                           bg=button_colour, activebackground=button_colour, fg='#ffffff', 
                           activeforeground='#ffffff', command=self.create_main_menu)
        
        credits_label = Label(self.credits_frame, text="Creator - Ollie O'Neill\nMusic - YouTube & Amazon Music\nCards - Vlad", 
                            font=(font, 50, 'bold'), relief=RAISED, bd=10, padx=20, bg=button_colour, fg='#ffffff')

        self.elements = {
            "back_button": back_button,
            "credits_label": credits_label,
            "frame": self.credits_frame,
        }

    def create_quit_menu(self):
        self.elements["back_button"].place(x=100, y=900)
        self.elements["credits_label"].place(relx=0.5, rely=0.5, anchor=CENTER)

    def create_main_menu(self):
        self.clear_screen()
        from scenes.main_menu import main_menu
        Main_Menu = main_menu(self.window, self.username, self.protecting)
        Main_Menu.run()

    def run(self):
        self.load_utils()
        self.create_quit_menu()