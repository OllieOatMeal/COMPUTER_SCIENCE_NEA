import sys
from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour
from Utils.json_handler import set_logged_in_user


def tkquit():
    sys.exit()


class quit_menu:
    def old_init(self):
        pass

    def __init__(self, window, username, protecting):
        self.window = window
        self.username = username
        self.protecting = protecting
        self.elements = {}
        self.main_background = None

    def clear_quit_screen(self):
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
        try:
            self.main_background = PhotoImage(file=main_background)
            bg = Label(self.window, image=self.main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self.elements["background"] = bg
        except Exception as e:
            print("Error loading background:", e)
            self.window.configure(bg=fall_back_colour)

        frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=400)
        self.elements["frame"] = frame

        label = Label(frame, text="Are you sure you want to quit?",
                      font=(font, 25, 'bold'), bg=button_colour, fg="white", bd=10, relief=RIDGE,
                      wraplength=600, justify="center")
        label.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.elements["label"] = label

        btn_no = Button(frame, text="NO", width=10, font=(font, 30, 'bold'),
                        bg=button_colour, fg="white", bd=10, relief=RIDGE,
                        activebackground=button_colour, activeforeground="white",
                        command=self.quit_unconfirm)
        btn_no.place(relx=0.5, rely=0.55, anchor=CENTER)
        self.elements["btn_no"] = btn_no

        btn_yes = Button(frame, text="YES", width=10, font=(font, 30, 'bold'),
                         bg=button_colour, fg="white", bd=10, relief=RIDGE,
                         activebackground=button_colour, activeforeground="white",
                         command=tkquit)
        btn_yes.place(relx=0.5, rely=0.85, anchor=CENTER)
        self.elements["btn_yes"] = btn_yes

    def quit_unconfirm(self):
        self.clear_quit_screen()
        from scenes.main_menu import main_menu
        main = main_menu(self.window, self.username, self.protecting)
        main.run()

    def save_current_user(self):
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        set_logged_in_user(username_value, protecting=self.protecting, encrypt=True)

    def run(self):
        self.load_utils()
        self.save_current_user()