from tkinter import *
from music import music
from variables import frame_colour, button_colour, font, main_background, fall_back_colour
import pygame
from Utils.json_handler import set_stored_music, get_music_volume, get_music_muted, set_music_volume, set_music_muted


class settings_scene:
    def __init__(self, window, username, protecting):
        self._window = window
        self._protecting = protecting
        self._elements = {}
        self._main_background = None
        self._username = username
        self._MUSIC_MUTED = False
        self._VOLUME = 50
        self._current_track = None

    def clear_settings_screen(self):
        for element in self._elements.values():
            element.place_forget()

    def load_utils(self):
        self._volume_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        self._volume_frame.place(relx=0.05, rely=0.15, anchor="w", width=1600, height=200)

        self._tracks_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        self._tracks_frame.place(relx=0.05, rely=0.35, anchor="w", width=1600, height=200)

        username = self._username
        if username != "admin":
            pass
        else:
            self._admin_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
            self._admin_frame.place(relx=0.05, rely=0.55, anchor="w", width=1600, height=200)
            current_user_slected = Label(self._admin_frame, text="", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg="#ffffff", width=300, height=50)
            current_user_slected.place(relx=0.05 ,rely=0.1 ,anchor="w")
            self._elements.update({
            "admin_frame": self._admin_frame,
            "current_user_selected": current_user_slected,
            })


        try:
            self._main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            background = Label(self._window, bg=fall_back_colour, bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            img_background = Label(self._window, image=self._main_background, bd=0)
            img_background.place(x=0, y=0)
            img_background.lower()
        back_button = Button(self._window, text="Back", width=10, font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='#ffffff', activeforeground='#ffffff', command=self.create_main_menu)
        stored_volume = get_music_volume()
        stored_muted = get_music_muted()
        if stored_volume is not None:
            self._VOLUME = stored_volume
            pygame.mixer.music.set_volume(self._VOLUME / 100)
        else:
            self._VOLUME = int(round(pygame.mixer.music.get_volume() * 100, 0))

        if stored_muted is not None:
            self._MUSIC_MUTED = stored_muted
            if self._MUSIC_MUTED:
                pygame.mixer.music.set_volume(0)

        volume_text = "MUSIC MUTED" if self._MUSIC_MUTED else f"Volume: {round(pygame.mixer.music.get_volume() * 100, 0)}%"
        volume_info_label = Label(self._volume_frame, text=volume_text, font=(font, 40, 'bold'), fg='#ffffff', bg=button_colour, relief=RAISED, bd=10)
        volumehigher = Button(self._volume_frame, text='Louder', font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='#ffffff', activeforeground='#ffffff', command=self.v_up)
        volumelower = Button(self._volume_frame, text='Quieter', font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='#ffffff', activeforeground='#ffffff', command=self.v_dn)
        mute_music_button = Button(self._volume_frame, text="Mute Music", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='#ffffff', activeforeground='#ffffff', command=self.v_tog)

        self._elements.update({
            "back_button": back_button,
            "volume_info_label": volume_info_label,
            "volume_higher_button": volumehigher,
            "volume_lower_button": volumelower,
            "mute_music_button": mute_music_button,
            "track_frame": self._tracks_frame,
            "volume_frame": self._volume_frame,
        }
        )

        for i in range(1, 9):
            track_button = Button(self._tracks_frame, text=f"# {i}", font=(font, 15, 'bold'), bg=button_colour, activebackground=button_colour, fg='#ffffff', activeforeground='#ffffff', relief=RAISED, bd=5, command=lambda i=i: self.change_track_with_highlight(i))
            self._elements[f"track_button_{i}"] = track_button

    def create_settings_menu(self):
        self._elements["back_button"].place(x=100, y=900)
        self._elements["volume_higher_button"].place(relx=0.25, rely=0.5, anchor=CENTER)
        self._elements["volume_lower_button"].place(relx=0.4, rely=0.5, anchor=CENTER)
        self._elements["volume_info_label"].place(relx=0.7, rely=0.5, anchor=CENTER)
        self._elements["mute_music_button"].place(relx=0.1, rely=0.5, anchor=CENTER)

        for i in range(1, 9):
            self._elements[f"track_button_{i}"].place(relx=0.025 + (i*0.1), rely=0.5, anchor="w")

    def update_track_button_colors(self):
        for i in range(1, 9):
            button = self._elements[f"track_button_{i}"]
            if i == self._current_track:
                button.config(bg="green", activebackground="green")
            else:
                button.config(bg=button_colour, activebackground=button_colour)

    def change_track_with_highlight(self, track_number):
        self._current_track = track_number
        music.change_track(self, track_number)
        self.update_track_button_colors()

    def v_up(self):
        music.volume_up(self)
        self._elements["volume_info_label"].config(text="Volume: " + str(round(pygame.mixer.music.get_volume() * 100, 0)) + "%")
        self._MUSIC_MUTED = False

    def v_dn(self):
        music.volume_down(self)
        self._elements["volume_info_label"].config(text="Volume: " + str(round(pygame.mixer.music.get_volume() * 100, 0)) + "%")
        self._MUSIC_MUTED = False

    def v_tog(self):
        music.toggle_music(self)
        if self._MUSIC_MUTED == True:
            self._elements["volume_info_label"].config(text="MUSIC MUTED")
        else:
            self._elements["volume_info_label"].config(text="Volume: " + str(round(pygame.mixer.music.get_volume() * 100, 0)) + "%")

    def create_main_menu(self):
        set_stored_music(self._current_track)
        set_music_volume(self._VOLUME)
        set_music_muted(self._MUSIC_MUTED)
        
        self.clear_settings_screen()
        from scenes.main_menu import main_menu
        Main_Menu = main_menu(self._window, self._username, self._protecting)
        Main_Menu.run()

    def run(self):
        self.load_utils()
        self.create_settings_menu()
        self.update_track_button_colors()