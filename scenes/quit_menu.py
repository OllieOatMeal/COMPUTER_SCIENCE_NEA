import sys
from tkinter import *
from variables import *
import json

def tkquit():
    sys.exit()

class quit_menu:
    def __init__(self, window, username):
        self.window = window
        self.username = username
        self.elements = {}
        self.main_background = None

    def clear_quit_screen(self):
        for element in self.elements.values():
            try:
                element.destroy()  # Fully remove the widget
            except:
                try:
                    element.place_forget()
                except:
                    pass
        self.elements.clear()

    def load_utils(self):
        # Background
        try:
            self.main_background = PhotoImage(file=main_background)
            bg = Label(self.window, image=self.main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self.elements["background"] = bg
        except Exception as e:
            print("Error loading background:", e)
            self.window.configure(bg='#1803A5')

        # Center frame
        frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=400)
        self.elements["frame"] = frame

        # Label
        label = Label(frame, text="Are you sure you want to quit?",
                      font=(font, 25, 'bold'), bg=button_colour, fg="white", bd=10, relief=RIDGE,
                      wraplength=600, justify="center")
        label.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.elements["label"] = label

        # NO button
        btn_no = Button(frame, text="NO", width=10, font=(font, 30, 'bold'),
                        bg=button_colour, fg="white", bd=10, relief=RIDGE,
                        activebackground=button_colour, activeforeground="white",
                        command=self.quit_unconfirm)
        btn_no.place(relx=0.5, rely=0.55, anchor=CENTER)
        self.elements["btn_no"] = btn_no

        # YES button
        btn_yes = Button(frame, text="YES", width=10, font=(font, 30, 'bold'),
                         bg=button_colour, fg="white", bd=10, relief=RIDGE,
                         activebackground=button_colour, activeforeground="white",
                         command=tkquit)
        btn_yes.place(relx=0.5, rely=0.85, anchor=CENTER)
        self.elements["btn_yes"] = btn_yes

    def quit_unconfirm(self):
        self.clear_quit_screen()
        from scenes.main_menu import main_menu
        main = main_menu(self.window, self.username)
        main.run()
    
    def save_current_user(self):
            data = json.dumps(({"logged_in_user": self.username.get()}), indent=4)
            with open("database\loaded_user.json", "w") as login_file:
                login_file.write(data)

    def run(self):
        self.load_utils()
        self.save_current_user()