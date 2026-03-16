"""

# Code to load the login scene

"""

"""
# Import nessicary functions/ procedures
"""
from tkinter import *
import random as r
from variables import path, card_path, font, button_colour, database_path, main_background, fall_back_colour
from Utils.db import increment_games_and_update_money, delete_user
from Utils.json_handler import save_json, LOADED_USER_PATH


"""
# Class where the cards are created
"""
class Card:
    # Initalises the class with the parameters passed in and set the base class specific values
    def __init__(self, name, value, image_path):
        self._name = name
        self._value = value
        self._hidden = True
        try:
            self._image = PhotoImage(file=image_path)
        except Exception as e:
            print(f"Failed to load image for {name}: {e}")
            self._image = None

    # Makes the card in a dictionary format
    def to_dict(self):
        return {
            "name": self._name,
            "value": self._value,
            "image": self._image
        }
"""
# Class where the cards are placed into a deck
"""
class Deck:
    # Initialises the class with parameters passed in and set the base class specific variables 
    def __init__(self):
        self._cards = []
        self._card_images = []
        self._card_back_image = None
        self.load_cards()
        self.shuffle()

    # Creates all the card objects and places them into the deck
    def load_cards(self):
        suits = ['S', 'D', 'C', 'H']
        ranks_values = {
            'A': 11, 'K': 10, 'Q': 10, 'J': 10,
            'T': 10, '9': 9, '8': 8, '7': 7,
            '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
        }
        try:
            self._card_back_image = PhotoImage(file=card_path+"\imgback.gif")
        except Exception as e:
            print(f"Failed to load card back image: {e}")
            self._card_back_image = None

        for suit in suits:
            for rank, value in ranks_values.items():
                card_name = f"{rank}{suit}"
                path = f"{card_path}/{card_name}.gif"
                card = Card(name=card_name, value=value, image_path=path)
                if card._image:
                    self._card_images.append(card._image)
                    self._cards.append(card.to_dict())
    
        print(len(self._cards))

    # Shuffles the cards that are in the deck
    def shuffle(self):
        n = len(self._cards)
        for i in range(n - 1, 0, -1):
            j = r.randint(0, i)
            self._cards[i], self._cards[j] = self._cards[j], self._cards[i]

    # Deals the top card from the deck
    def deal_card(self):
        if self._cards:
            return self._cards.pop(0)
        return None

    # Resets the deck
    def reset_deck(self):
        self._cards.clear()
        self._card_images.clear()
        self.load_cards()
        self.shuffle()

"""
# Main class to control the scene
"""
class singleplayer:
    # Initialises the class with parameters passed in and set the base class specific variables 
    def __init__(self, window, username, balance, protecting):
        self._window = window
        self._username = username
        self._balance = balance
        self._protecting = protecting
        self._elements = {}
        self._background = None
        self._main_deck = None

        self._user_deck = []
        self._dealer_deck = []

        self._user_val = 0
        self._bet = 10
        self._split_mode = False
        self._split_hands = []
        self._current_hand_idx = 0
        self._bets = []
        self._doubled = False

    def clear_screen(self):
        for element in self._elements.values():
            try:
                if element.winfo_exists():
                    element.place_forget()
            except Exception as e:
                print(f"Widget removal error: {e}")

    def load_utils(self):
        try:
            self._background = PhotoImage(file=main_background)
            bg_label = Label(self._window, image=self._background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self._window.configure(bg=fall_back_colour)

        self._elements["exit_button"] = Button(
            self._window, text="Exit", font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff', activebackground=button_colour, activeforeground='#ffffff',
            command=self.save_and_exit
        )
        main_deck = Deck()
        self._card_back_image = main_deck._card_back_image

        for i in range(1, 11):
            if self._card_back_image:
                self._elements[f"static_deck_{i}"] = Label(self._window, image=self._card_back_image)
            else:
                self._elements[f"static_deck_{i}"] = Label(self._window, text="Back", bg="gray", width=10, height=5)

        self._elements["double_button"] = Button(self._window, text="Double", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.double_down)
        self._elements["split_button"] = Button(self._window, text="Split", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.split_hand)


    def save_and_exit(self):
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username

        success = increment_games_and_update_money(username_value, self._balance, self._protecting)
        if not success:
            print("Database error while saving money/games played")

        from scenes.main_menu import main_menu
        self.clear_screen()
        Main_Menu = main_menu(self._window, username_value, self._protecting)
        Main_Menu.run()

    def deal_cards(self):
        self._user_deck = []
        self._dealer_deck = []
        for _ in range(2):
            user_card = self._main_deck.deal_card()
            dealer_card = self._main_deck.deal_card()
            if user_card:
                self._user_deck.append(user_card)
            if dealer_card:
                self._dealer_deck.append(dealer_card)

    def get_hand_value(self, hand):
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['name'].startswith('A'))
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def update_ui(self):
        for key in list(self._elements.keys()):
            if key.startswith("card_slot_") or key.startswith("dealer_slot_") or key in ["player_total_label", "dealer_total_label"]:
                self._elements[key].place_forget()
                del self._elements[key]

        screen_width = self._window.winfo_screenwidth()
        max_cards = max(len(self._user_deck), len(self._dealer_deck), 1)
        spacing = max(40, min(120, (screen_width - 200) // (max_cards + 1)))
        start_card_x = 50
        start_count_x = 50
        y_player_card = 650
        y_dealer_card = 300
        y_player_count = 600
        y_dealer_count = 250

        if self._split_mode:
            for i, card in enumerate(self._split_hands[0], 1):
                if card['image']:
                    lbl = Label(self._window, image=card['image'])
                else:
                    lbl = Label(self._window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=start_card_x + (i - 1) * spacing, y=y_player_card)
                self._elements[f"card_slot_0_{i}"] = lbl
            hand2_start_x = start_card_x + 450
            for i, card in enumerate(self._split_hands[1], 1):
                if card['image']:
                    lbl = Label(self._window, image=card['image'])
                else:
                    lbl = Label(self._window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=hand2_start_x + (i - 1) * spacing, y=y_player_card)
                self._elements[f"card_slot_1_{i}"] = lbl
        else:
            for i, card in enumerate(self._user_deck, 1):
                if card['image']:
                    lbl = Label(self._window, image=card['image'])
                else:
                    lbl = Label(self._window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=start_card_x + (i - 1) * spacing, y=y_player_card)
                self._elements[f"card_slot_{i}"] = lbl

        for i, card in enumerate(self._dealer_deck, 1):
            if self._game_over or i == 1:
                img = card['image']
            else:
                img = self._card_back_image
            if img:
                lbl = Label(self._window, image=img)
            else:
                lbl = Label(self._window, text=card['name'], bg="gray", width=8, height=5)
            lbl.place(x=start_card_x + (i - 1) * spacing, y=y_dealer_card)
            self._elements[f"dealer_slot_{i}"] = lbl

        if self._split_mode:
            total1 = self.get_hand_value(self._split_hands[0])
            total2 = self.get_hand_value(self._split_hands[1])
            txt = f"Hand 1: {total1}          Hand 2: {total2}"
        else:
            total1 = self.get_hand_value(self._user_deck)
            txt = f"Player Total: {total1}"
        self._elements["player_total_label"] = Label(
            self._window, text=txt, font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white'
        )
        self._elements["player_total_label"].place(x=(start_count_x), y=y_player_count)

        if self._game_over:
            dealer_total = self.get_hand_value(self._dealer_deck)
        else:
            dealer_total = self._dealer_deck[0]['value'] if self._dealer_deck else 0
        self._elements["dealer_total_label"] = Label(
            self._window, text=f"Dealer Total: {dealer_total}", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white'
        )
        self._elements["dealer_total_label"].place(x=(start_count_x), y=y_dealer_count)

        if "balance_label" in self._elements:
            self._elements["balance_label"].config(text=f"Balance: ${self._balance}")

    def hit(self):
        if self._game_over:
            return
        card = self._main_deck.deal_card()
        if card:
            if self._split_mode:
                self._split_hands[self._current_hand_idx].append(card)
                self.update_ui()
                if self.get_hand_value(self._split_hands[self._current_hand_idx]) > 21:
                    self._elements.get("result_label") and self._elements["result_label"].destroy()
                    self._elements["result_label"] = Label(self._window, text="Bust!", font=(font, 40, 'bold'), bg=button_colour, fg='white')
                    self._elements["result_label"].place(x=700, y=75)
                    if self._current_hand_idx == 0:
                        self._current_hand_idx = 1
                    else:
                        self._game_over = True
                        self.dealer_play()
            else:
                self._user_deck.append(card)
                self.update_ui()
                if self.get_hand_value(self._user_deck) > 21:
                    self.end_game("Bust! Dealer wins.")

    def stand(self):
        if self._game_over:
            return
        if self._split_mode:
            if self._current_hand_idx == 0:
                self._current_hand_idx = 1
                return
            else:
                self._game_over = True
                self.dealer_play()
                return

        while self.get_hand_value(self._dealer_deck) < 17:
            card = self._main_deck.deal_card()
            if card:
                self._dealer_deck.append(card)
        self.update_ui()
        self.check_winner()

    def dealer_play(self):
        while self.get_hand_value(self._dealer_deck) < 17:
            card = self._main_deck.deal_card()
            if card:
                self._dealer_deck.append(card)
        self.update_ui()
        if self._split_mode:
            results = []
            dealer_val = self.get_hand_value(self._dealer_deck)
            for idx, hand in enumerate(self._split_hands):
                user_val = self.get_hand_value(hand)
                bet = self._bets[idx]
                if user_val > 21:
                    self._balance -= 0
                    results.append((idx, 'lose'))
                elif dealer_val > 21 or user_val > dealer_val:
                    self._balance += bet
                    results.append((idx, 'win'))
                elif user_val < dealer_val:
                    self._balance -= bet
                    results.append((idx, 'lose'))
                else:
                    results.append((idx, 'push'))
            self._elements.get("result_label") and self._elements["result_label"].destroy()
            res_text = ", ".join([f"Hand {i+1}:{r}" for i, r in results])
            result = Label(self._window, text=res_text, font=(font, 30, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
            result.place(x=500, y=75)
            self._elements["result_label"] = result
        else:
            self.check_winner()

    def check_winner(self):
        user_val = self.get_hand_value(self._user_deck)
        self._user_val = user_val
        dealer_val = self.get_hand_value(self._dealer_deck)
        if dealer_val > 21 or user_val > dealer_val:
            self.end_game("You win!", win=True)
        elif user_val < dealer_val:
            self.end_game("Dealer wins.")
        else:
            self.end_game("Push (Draw).")

    def end_game(self, message, win=False):
        if self._user_val == 21 and len(self._user_deck) == 2:
            self._balance += 500
        else:
            factor = r.randint(1, 100)
            self._game_over = True
            if win:
                self._balance += (10*factor)
            else:
                self._balance -= (10*factor)
                if self._balance <= 0:
                    self._balance = 0
                else:
                    pass

        self.update_ui()
        result = Label(self._window, text=message, font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
        result.place(x=700, y=75)
        self._elements["result_label"] = result
        play_again = Button(self._window, text="Play Again", font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.play_again)
        play_again.place(x=250, y=50)
        self._elements["play_again"] = play_again

    def play_again(self):
        self.check_bal()
        if "result_label" in self._elements:
            self._elements["result_label"].destroy()
            del self._elements["result_label"]
        if "play_again" in self._elements:
            self._elements["play_again"].destroy()
            del self._elements["play_again"]
        self._user_deck = []
        self._dealer_deck = []
        self._main_deck.reset_deck()
        self._game_over = False
        self._split_mode = False
        self._split_hands = []
        self._current_hand_idx = 0
        self._bets = []
        self._doubled = False
        self.deal_cards()
        self.update_ui()

    def remove_card_and_total_widgets(self):
        for key in list(self._elements.keys()):
            try:
                if key.startswith("card_slot_") or key.startswith("dealer_slot_"):
                    widget = self._elements.get(key)
                    if widget:
                        try:
                            widget.destroy()
                        except Exception as e:
                            print(f"Failed to destroy widget {key}: {e}")
                    del self._elements[key]
            except Exception as e:
                print(f"Error removing {key}: {e}")

        for lbl_key in ("player_total_label", "dealer_total_label"):
            try:
                if lbl_key in self._elements:
                    widget = self._elements.get(lbl_key)
                    if widget:
                        try:
                            widget.destroy()
                        except Exception as e:
                            print(f"Failed to destroy widget {lbl_key}: {e}")
                    del self._elements[lbl_key]
            except Exception as e:
                print(f"Error removing {lbl_key}: {e}")

    def check_bal(self):
        if self._balance <= 0:
            username_value = self._username.get() if hasattr(self._username, 'get') else self._username

            success = delete_user(username_value, self._protecting)
            if not success:
                print("Database error while deleting user")

            try:
                save_json(LOADED_USER_PATH, {})
            except Exception as e:
                print(f"Error clearing loaded_user.json: {e}")

            for widget in self._window.winfo_children():
                widget.destroy()

            from scenes.login_scene import login
            Login_Scene = login(self._window, self._protecting)
            Login_Scene.acc_deleted()
        else:
            return

    def create_screen(self):
        self._elements["exit_button"].place(x=50, y=50)
        if "balance_label" in self._elements:
            self._elements["balance_label"].place(x=50, y=1000)
        if "hit_button" in self._elements:
            self._elements["hit_button"].place(x=900, y=1000)
        if "stand_button" in self._elements:
            self._elements["stand_button"].place(x=1000, y=1000)
        if "double_button" in self._elements:
            self._elements["double_button"].place(x=1150, y=1000)
        if "split_button" in self._elements:
            self._elements["split_button"].place(x=1350, y=1000)
        screenheight = self._window.winfo_screenheight()
        start_y = screenheight // 2 - 200

    def run(self):
        self._main_deck = Deck()
        self.load_utils()
        self._elements["balance_label"] = Label(self._window, text=f"Balance: ${self._balance}", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
        self._elements["hit_button"] = Button(self._window, text="Hit", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.hit)
        self._elements["stand_button"] = Button(self._window, text="Stand", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.stand)
        self.create_screen()
        self._user_deck = []
        self._dealer_deck = []
        self._game_over = False
        self.deal_cards()
        self.update_ui()

    def double_down(self):
        if self._split_mode:
            hand = self._split_hands[self._current_hand_idx]
            if len(hand) != 2:
                return
            try:
                if self._balance < self._bets[self._current_hand_idx]:
                    return
            except Exception:
                return
            self._bets[self._current_hand_idx] *= 2
            card = self._main_deck.deal_card()
            if card:
                hand.append(card)
                self.update_ui()
            if self._current_hand_idx == 0:
                self._current_hand_idx = 1
            else:
                self._game_over = True
                self.dealer_play()
        else:
            if len(self._user_deck) != 2:
                return
            if self._balance < self._bet:
                return
            self._bet *= 2
            card = self._main_deck.deal_card()
            if card:
                self._user_deck.append(card)
                self.update_ui()
            self._game_over = True
            self.dealer_play()

    def split_hand(self):
        if len(self._user_deck) != 2:
            return
        first_card = self._user_deck[0]['name'][0]
        second_card = self._user_deck[1]['name'][0]
        if first_card != second_card:
            return
        if self._balance < self._bet:
            return
        self._split_mode = True
        self._split_hands = [[self._user_deck[0]], [self._user_deck[1]]]
        self._bets = [self._bet, self._bet]
        self._balance -= self._bet
        self._current_hand_idx = 0
        self.update_ui()