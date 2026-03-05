from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour


class multiplayer:
    def __init__(self, window, username, balance, protecting):
        self._window = window
        self._username = username
        self._balance = balance
        self._elements = {}
        self._protecting = protecting

    def clear_screen(self):
        for element in self._elements.values():
            element.place_forget()

    def load_utils(self):
        try:
            self._main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self._window, bg=fall_back_colour, bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
            background.lower()
        else:
            self._img_background = Label(self._window, image=self._main_background, bd=0)
            self._img_background.place(x=0, y=0)

        mp_frame = Frame(self._window, width=1500, height=720, bg=frame_colour, bd=10, relief=RAISED)
        mp_frame.place(relx=0.5, rely=0.6, anchor=CENTER)
        mp_frame.lift()
        self._elements["mp_frame"] = mp_frame

        self._elements["mp_label"] = Label(mp_frame, text="Sorry there is no Multiplayer Mode currently. \nPlease check back later.", font=(font, 30, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        self._elements["exit_button"] = Button(mp_frame, text="Exit", font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', activebackground=button_colour, activeforeground='#ffffff', command=self.back_to_main_menu)

        self._elements["mp_label"].place(relx=0.5, rely=0.4, anchor=CENTER)
        self._elements["exit_button"].place(relx=0.05, rely=0.8, anchor='w', width=200, height=100)

        for element in self._elements.values():
            element.lift()

    def back_to_main_menu(self):
        from scenes.main_menu import main_menu
        self.clear_screen()
        main_meu = main_menu(self._window, self._username, self._protecting)
        main_meu.run()

    def run(self):
        self.load_utils()