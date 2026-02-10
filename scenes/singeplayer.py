from tkinter import *
import random as r
from variables import path, card_path, font, button_colour, database_path, main_background, fall_back_colour
from Utils.db import increment_games_and_update_money, delete_user
from Utils.json_handler import save_json, LOADED_USER_PATH

class Card:
    def __init__(self, name, value, image_path):
        self.name = name
        self.value = value
        self.hidden = True
        try:
            self.image = PhotoImage(file=image_path)
        except Exception as e:
            print(f"Failed to load image for {name}: {e}")
            self.image = None

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "image": self.image
        }

class Deck:
    def __init__(self):
        self.cards = []
        self.card_images = []
        self.card_back_image = None
        self.load_cards()
        self.shuffle()

    def load_cards(self):
        suits = ['S', 'D', 'C', 'H']
        ranks_values = {
            'A': 11, 'K': 10, 'Q': 10, 'J': 10,
            'T': 10, '9': 9, '8': 8, '7': 7,
            '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
        }
        try:
            self.card_back_image = PhotoImage(file=card_path+"\imgback.gif")
        except Exception as e:
            print(f"Failed to load card back image: {e}")
            self.card_back_image = None

        for suit in suits:
            for rank, value in ranks_values.items():
                card_name = f"{rank}{suit}"
                path = f"{card_path}/{card_name}.gif"
                card = Card(name=card_name, value=value, image_path=path)
                if card.image:
                    self.card_images.append(card.image)
                    self.cards.append(card.to_dict())

    def shuffle(self):
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = r.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def deal_card(self):
        if self.cards:
            return self.cards.pop(0)
        return None

    def reset_deck(self):
        self.cards.clear()
        self.card_images.clear()
        self.load_cards()
        self.shuffle()

class singleplayer:
    def __init__(self, window, username, balance, protecting):
        self.window = window
        self.username = username
        self.balance = balance
        self.protecting = protecting
        self.elements = {}
        self.background = None
        self.main_deck = None

        self.user_deck = []
        self.dealer_deck = []

        self.user_val = 0
        self.bet = 10
        self.split_mode = False
        self.split_hands = []
        self.current_hand_idx = 0
        self.bets = []
        self.doubled = False

    def clear_screen(self):
        for element in self.elements.values():
            try:
                if element.winfo_exists():
                    element.place_forget()
            except Exception as e:
                print(f"Widget removal error: {e}")

    def load_utils(self):
        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg=fall_back_colour)

        self.elements["exit_button"] = Button(
            self.window, text="Exit", font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff', activebackground=button_colour, activeforeground='#ffffff',
            command=self.save_and_exit
        )
        main_deck = Deck()
        self.card_back_image = main_deck.card_back_image

        for i in range(1, 11):
            if self.card_back_image:
                self.elements[f"static_deck_{i}"] = Label(self.window, image=self.card_back_image)
            else:
                self.elements[f"static_deck_{i}"] = Label(self.window, text="Back", bg="gray", width=10, height=5)

        self.elements["double_button"] = Button(self.window, text="Double", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.double_down)
        self.elements["split_button"] = Button(self.window, text="Split", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.split_hand)


    def save_and_exit(self):
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        success = increment_games_and_update_money(username_value, self.balance, self.protecting)
        if not success:
            print("Database error while saving money/games played")

        from scenes.main_menu import main_menu
        self.clear_screen()
        Main_Menu = main_menu(self.window, username_value, self.protecting)
        Main_Menu.run()

    def deal_cards(self):
        self.user_deck = []
        self.dealer_deck = []
        for _ in range(2):
            user_card = self.main_deck.deal_card()
            dealer_card = self.main_deck.deal_card()
            if user_card:
                self.user_deck.append(user_card)
            if dealer_card:
                self.dealer_deck.append(dealer_card)

    def get_hand_value(self, hand):
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['name'].startswith('A'))
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def update_ui(self):
        for key in list(self.elements.keys()):
            if key.startswith("card_slot_") or key.startswith("dealer_slot_") or key in ["player_total_label", "dealer_total_label"]:
                self.elements[key].place_forget()
                del self.elements[key]

        screen_width = self.window.winfo_screenwidth()
        max_cards = max(len(self.user_deck), len(self.dealer_deck), 1)
        spacing = max(40, min(120, (screen_width - 200) // (max_cards + 1)))
        start_card_x = 50
        start_count_x = 50
        y_player_card = 650
        y_dealer_card = 300
        y_player_count = 600
        y_dealer_count = 250

        if self.split_mode:
            for i, card in enumerate(self.split_hands[0], 1):
                if card['image']:
                    lbl = Label(self.window, image=card['image'])
                else:
                    lbl = Label(self.window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=start_card_x + (i - 1) * spacing, y=y_player_card)
                self.elements[f"card_slot_0_{i}"] = lbl
            hand2_start_x = start_card_x + 450
            for i, card in enumerate(self.split_hands[1], 1):
                if card['image']:
                    lbl = Label(self.window, image=card['image'])
                else:
                    lbl = Label(self.window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=hand2_start_x + (i - 1) * spacing, y=y_player_card)
                self.elements[f"card_slot_1_{i}"] = lbl
        else:
            for i, card in enumerate(self.user_deck, 1):
                if card['image']:
                    lbl = Label(self.window, image=card['image'])
                else:
                    lbl = Label(self.window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=start_card_x + (i - 1) * spacing, y=y_player_card)
                self.elements[f"card_slot_{i}"] = lbl

        for i, card in enumerate(self.dealer_deck, 1):
            if self.game_over or i == 1:
                img = card['image']
            else:
                img = self.card_back_image
            if img:
                lbl = Label(self.window, image=img)
            else:
                lbl = Label(self.window, text=card['name'], bg="gray", width=8, height=5)
            lbl.place(x=start_card_x + (i - 1) * spacing, y=y_dealer_card)
            self.elements[f"dealer_slot_{i}"] = lbl

        if self.split_mode:
            total1 = self.get_hand_value(self.split_hands[0])
            total2 = self.get_hand_value(self.split_hands[1])
            txt = f"Hand1: {total1}          Hand2: {total2}"
        else:
            total1 = self.get_hand_value(self.user_deck)
            txt = f"Player Total: {total1}"
        self.elements["player_total_label"] = Label(
            self.window, text=txt, font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white'
        )
        self.elements["player_total_label"].place(x=(start_count_x), y=y_player_count)

        if self.game_over:
            dealer_total = self.get_hand_value(self.dealer_deck)
        else:
            dealer_total = self.dealer_deck[0]['value'] if self.dealer_deck else 0
        self.elements["dealer_total_label"] = Label(
            self.window, text=f"Dealer Total: {dealer_total}", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white'
        )
        self.elements["dealer_total_label"].place(x=(start_count_x), y=y_dealer_count)

        if "balance_label" in self.elements:
            self.elements["balance_label"].config(text=f"Balance: ${self.balance}")

    def hit(self):
        if self.game_over:
            return
        card = self.main_deck.deal_card()
        if card:
            if self.split_mode:
                self.split_hands[self.current_hand_idx].append(card)
                self.update_ui()
                if self.get_hand_value(self.split_hands[self.current_hand_idx]) > 21:
                    self.elements.get("result_label") and self.elements["result_label"].destroy()
                    self.elements["result_label"] = Label(self.window, text="Bust!", font=(font, 40, 'bold'), bg=button_colour, fg='white')
                    self.elements["result_label"].place(x=700, y=75)
                    if self.current_hand_idx == 0:
                        self.current_hand_idx = 1
                    else:
                        self.game_over = True
                        self.dealer_play()
            else:
                self.user_deck.append(card)
                self.update_ui()
                if self.get_hand_value(self.user_deck) > 21:
                    self.end_game("Bust! Dealer wins.")

    def stand(self):
        if self.game_over:
            return
        if self.split_mode:
            if self.current_hand_idx == 0:
                self.current_hand_idx = 1
                return
            else:
                self.game_over = True
                self.dealer_play()
                return

        while self.get_hand_value(self.dealer_deck) < 17:
            card = self.main_deck.deal_card()
            if card:
                self.dealer_deck.append(card)
        self.update_ui()
        self.check_winner()

    def dealer_play(self):
        while self.get_hand_value(self.dealer_deck) < 17:
            card = self.main_deck.deal_card()
            if card:
                self.dealer_deck.append(card)
        self.update_ui()
        if self.split_mode:
            results = []
            dealer_val = self.get_hand_value(self.dealer_deck)
            for idx, hand in enumerate(self.split_hands):
                user_val = self.get_hand_value(hand)
                bet = self.bets[idx]
                if user_val > 21:
                    self.balance -= 0
                    results.append((idx, 'lose'))
                elif dealer_val > 21 or user_val > dealer_val:
                    self.balance += bet
                    results.append((idx, 'win'))
                elif user_val < dealer_val:
                    self.balance -= bet
                    results.append((idx, 'lose'))
                else:
                    results.append((idx, 'push'))
            self.elements.get("result_label") and self.elements["result_label"].destroy()
            res_text = ", ".join([f"Hand {i+1}:{r}" for i, r in results])
            result = Label(self.window, text=res_text, font=(font, 30, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
            result.place(x=500, y=75)
            self.elements["result_label"] = result
        else:
            self.check_winner()

    def check_winner(self):
        user_val = self.get_hand_value(self.user_deck)
        self.user_val = user_val
        dealer_val = self.get_hand_value(self.dealer_deck)
        if dealer_val > 21 or user_val > dealer_val:
            self.end_game("You win!", win=True)
        elif user_val < dealer_val:
            self.end_game("Dealer wins.")
        else:
            self.end_game("Push (Draw).")

    def end_game(self, message, win=False):
        if self.user_val == 21 and len(self.user_deck) == 2:
            self.balance += 500
        else:
            factor = r.randint(1, 100)
            self.game_over = True
            if win:
                self.balance += (10*factor)
            else:
                self.balance -= (10*factor)
                if self.balance <= 0:
                    self.balance = 0
                else:
                    pass

        self.update_ui()
        result = Label(self.window, text=message, font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
        result.place(x=700, y=75)
        self.elements["result_label"] = result
        play_again = Button(self.window, text="Play Again", font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.play_again)
        play_again.place(x=250, y=50)
        self.elements["play_again"] = play_again

    def play_again(self):
        self.check_bal()
        if "result_label" in self.elements:
            self.elements["result_label"].destroy()
            del self.elements["result_label"]
        if "play_again" in self.elements:
            self.elements["play_again"].destroy()
            del self.elements["play_again"]
        self.user_deck = []
        self.dealer_deck = []
        self.main_deck.reset_deck()
        self.game_over = False
        self.split_mode = False
        self.split_hands = []
        self.current_hand_idx = 0
        self.bets = []
        self.doubled = False
        self.deal_cards()
        self.update_ui()

    def remove_card_and_total_widgets(self):
        for key in list(self.elements.keys()):
            try:
                if key.startswith("card_slot_") or key.startswith("dealer_slot_"):
                    widget = self.elements.get(key)
                    if widget:
                        try:
                            widget.destroy()
                        except Exception as e:
                            print(f"Failed to destroy widget {key}: {e}")
                    del self.elements[key]
            except Exception as e:
                print(f"Error removing {key}: {e}")

        for lbl_key in ("player_total_label", "dealer_total_label"):
            try:
                if lbl_key in self.elements:
                    widget = self.elements.get(lbl_key)
                    if widget:
                        try:
                            widget.destroy()
                        except Exception as e:
                            print(f"Failed to destroy widget {lbl_key}: {e}")
                    del self.elements[lbl_key]
            except Exception as e:
                print(f"Error removing {lbl_key}: {e}")

    def check_bal(self):
        if self.balance <= 0:
            username_value = self.username.get() if hasattr(self.username, 'get') else self.username

            success = delete_user(username_value, self.protecting)
            if not success:
                print("Database error while deleting user")

            try:
                save_json(LOADED_USER_PATH, {})
            except Exception as e:
                print(f"Error clearing loaded_user.json: {e}")

            for widget in self.window.winfo_children():
                widget.destroy()

            from scenes.login_scene import login
            Login_Scene = login(self.window, self.protecting)
            Login_Scene.acc_deleted()
        else:
            return

    def create_screen(self):
        self.elements["exit_button"].place(x=50, y=50)
        if "balance_label" in self.elements:
            self.elements["balance_label"].place(x=50, y=1000)
        if "hit_button" in self.elements:
            self.elements["hit_button"].place(x=900, y=1000)
        if "stand_button" in self.elements:
            self.elements["stand_button"].place(x=1000, y=1000)
        if "double_button" in self.elements:
            self.elements["double_button"].place(x=1150, y=1000)
        if "split_button" in self.elements:
            self.elements["split_button"].place(x=1350, y=1000)
        screenheight = self.window.winfo_screenheight()
        start_y = screenheight // 2 - 200

    def run(self):
        self.main_deck = Deck()
        self.main_deck.load_cards()
        self.load_utils()
        self.elements["balance_label"] = Label(self.window, text=f"Balance: ${self.balance}", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
        self.elements["hit_button"] = Button(self.window, text="Hit", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.hit)
        self.elements["stand_button"] = Button(self.window, text="Stand", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.stand)
        self.create_screen()
        self.user_deck = []
        self.dealer_deck = []
        self.game_over = False
        self.deal_cards()
        self.update_ui()

    def double_down(self):
        if self.split_mode:
            hand = self.split_hands[self.current_hand_idx]
            if len(hand) != 2:
                return
            try:
                if self.balance < self.bets[self.current_hand_idx]:
                    return
            except Exception:
                return
            self.bets[self.current_hand_idx] *= 2
            card = self.main_deck.deal_card()
            if card:
                hand.append(card)
                self.update_ui()
            if self.current_hand_idx == 0:
                self.current_hand_idx = 1
            else:
                self.game_over = True
                self.dealer_play()
        else:
            if len(self.user_deck) != 2:
                return
            if self.balance < self.bet:
                return
            self.bet *= 2
            card = self.main_deck.deal_card()
            if card:
                self.user_deck.append(card)
                self.update_ui()
            self.game_over = True
            self.dealer_play()

    def split_hand(self):
        if len(self.user_deck) != 2:
            return
        first_card = self.user_deck[0]['name'][0]
        second_card = self.user_deck[1]['name'][0]
        if first_card != second_card:
            return
        if self.balance < self.bet:
            return
        self.split_mode = True
        self.split_hands = [[self.user_deck[0]], [self.user_deck[1]]]
        self.bets = [self.bet, self.bet]
        self.balance -= self.bet
        self.current_hand_idx = 0
        self.update_ui()