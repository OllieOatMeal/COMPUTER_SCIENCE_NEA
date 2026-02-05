"""
Singleplayer blackjack game
Handles all the game logic, betting, dealing cards, etc.
"""

from tkinter import *
import random as r
from variables import path, card_path, font, button_colour, database_path, main_background, fall_back_colour
from Utils.db import increment_games_and_update_money, delete_user
from Utils.json_handler import save_json, LOADED_USER_PATH


# A playing card with a name, value, and image
class Card:
    """A single card in the deck"""
    def __init__(self, name, value, image_path):
        self.name = name
        self.value = value
        self.hidden = True
        try:
            self.image = PhotoImage(file=image_path)  # Load card image
        except Exception as e:
            print(f"Failed to load image for {name}: {e}")
            self.image = None

    def to_dict(self):
        # Returns card info as a dictionary
        return {
            "name": self.name,
            "value": self.value,
            "image": self.image
        }

# Represents a deck of cards
class Deck:
    def __init__(self):
        self.cards = []
        self.card_images = []  # Prevent garbage collection of PhotoImage
        self.card_back_image = None
        self.load_cards()
        self.shuffle()

    def load_cards(self):
        # Loads all cards into the deck with images
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
                    self.card_images.append(card.image)  # Store reference to prevent GC
                    self.cards.append(card.to_dict())

    def shuffle(self):
        # Shuffles the deck using Fisher-Yates algorithm
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = r.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def deal_card(self):
        # Deals (removes and returns) the top card from the deck
        if self.cards:
            return self.cards.pop(0)
        return None

    def reset_deck(self):
        # Resets and reshuffles the deck
        self.cards.clear()
        self.card_images.clear()
        self.load_cards()
        self.shuffle()

# Main singleplayer blackjack game class
class singleplayer:
    def __init__(self, window, username, balance, protecting):
        self.window = window
        self.username = username
        self.balance = balance
        self.protecting = protecting
        self.elements = {}         # Stores all UI elements
        self.background = None
        self.main_deck = None

        self.user_deck = []        # Player's hand
        self.dealer_deck = []      # Dealer's hand

        self.user_val = 0
        # Blackjack-specific state
        self.bet = 10
        self.split_mode = False
        self.split_hands = []  # list of hands when split
        self.current_hand_idx = 0
        self.bets = []  # bet per hand
        self.doubled = False

    def clear_screen(self):
        # Removes all widgets from the screen
        for element in self.elements.values():
            try:
                if element.winfo_exists():
                    element.place_forget()
            except Exception as e:
                print(f"Widget removal error: {e}")

    def load_utils(self):
        # Loads background and static UI elements
        try:
            self.background = PhotoImage(file=main_background)
            bg_label = Label(self.window, image=self.background)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.window.configure(bg=fall_back_colour)  # fallback background color

        # Exit button
        self.elements["exit_button"] = Button(
            self.window, text="Exit", font=(font, 40, 'bold'), relief=RAISED, bd=10,
            bg=button_colour, fg='#ffffff', activebackground=button_colour, activeforeground='#ffffff',
            command=self.save_and_exit
        )
        main_deck = Deck()  # create a deck instance here if not passed in
        self.card_back_image = main_deck.card_back_image  # store for use later

        # Static deck images (for visual effect)
        for i in range(1, 11):
            if self.card_back_image:
                self.elements[f"static_deck_{i}"] = Label(self.window, image=self.card_back_image)
            else:
                self.elements[f"static_deck_{i}"] = Label(self.window, text="Back", bg="gray", width=10, height=5)

        # Action buttons
        self.elements["double_button"] = Button(self.window, text="Double", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.double_down)
        self.elements["split_button"] = Button(self.window, text="Split", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', command=self.split_hand)


    def save_and_exit(self):
        # Saves balance and games played to the database, then returns to main menu
        # Determine actual username string (supports StringVar or plain str)
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        # Persist new balance and increment games played via Utils.db
        success = increment_games_and_update_money(username_value, self.balance, self.protecting)
        if not success:
            print("Database error while saving money/games played")

        # Return to main menu
        from scenes.main_menu import main_menu
        self.clear_screen()  # Clear current game UI
        Main_Menu = main_menu(self.window, username_value, self.protecting)
        Main_Menu.run()

    def deal_cards(self):
        # Deals two cards each to player and dealer at the start of a round
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
        # Calculates the value of a hand, handling Aces as 1 or 11
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['name'].startswith('A'))
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def update_ui(self):
        # Remove old card and total labels if any
        for key in list(self.elements.keys()):
            if key.startswith("card_slot_") or key.startswith("dealer_slot_") or key in ["player_total_label", "dealer_total_label"]:
                self.elements[key].place_forget()
                del self.elements[key]

        # Calculate spacing so cards fit on screen
        screen_width = self.window.winfo_screenwidth()
        max_cards = max(len(self.user_deck), len(self.dealer_deck), 1)
        spacing = max(40, min(120, (screen_width - 200) // (max_cards + 1)))
        start_card_x = 50
        start_count_x = 50
        # Positioning for split or single hand
        y_player_card = 650
        y_dealer_card = 300
        y_player_count = 600
        y_dealer_count = 250

        # Player cards (support split hands)
        if self.split_mode:
            # draw first hand on left side
            for i, card in enumerate(self.split_hands[0], 1):
                if card['image']:
                    lbl = Label(self.window, image=card['image'])
                else:
                    lbl = Label(self.window, text=card['name'], bg="gray", width=8, height=5)
                lbl.place(x=start_card_x + (i - 1) * spacing, y=y_player_card)
                self.elements[f"card_slot_0_{i}"] = lbl
            # draw second hand on right side (wider horizontal separation)
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

        # Dealer cards
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

        # Player total label (show for split or single)
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

        # Dealer total label
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
        # Player draws a card
        if self.game_over:
            return
        card = self.main_deck.deal_card()
        if card:
            # operate on current hand (support split)
            if self.split_mode:
                self.split_hands[self.current_hand_idx].append(card)
                self.update_ui()
                if self.get_hand_value(self.split_hands[self.current_hand_idx]) > 21:
                    # bust this hand
                    self.elements.get("result_label") and self.elements["result_label"].destroy()
                    self.elements["result_label"] = Label(self.window, text="Bust!", font=(font, 40, 'bold'), bg=button_colour, fg='white')
                    self.elements["result_label"].place(x=700, y=75)
                    # move to next hand or finish
                    if self.current_hand_idx == 0:
                        self.current_hand_idx = 1
                    else:
                        # both hands over -> dealer plays
                        self.game_over = True
                        self.dealer_play()
            else:
                self.user_deck.append(card)
                self.update_ui()
                if self.get_hand_value(self.user_deck) > 21:
                    self.end_game("Bust! Dealer wins.")

    def stand(self):
        # Player stands, dealer draws until 17 or higher
        if self.game_over:
            return
        if self.split_mode:
            # finish current hand, move to next or finish
            if self.current_hand_idx == 0:
                self.current_hand_idx = 1
                # continue playing second hand
                return
            else:
                # both hands done -> dealer plays
                self.game_over = True
                self.dealer_play()
                return

        # non-split: dealer plays
        while self.get_hand_value(self.dealer_deck) < 17:
            card = self.main_deck.deal_card()
            if card:
                self.dealer_deck.append(card)
        self.update_ui()
        self.check_winner()

    def dealer_play(self):
        # Dealer draws until 17
        while self.get_hand_value(self.dealer_deck) < 17:
            card = self.main_deck.deal_card()
            if card:
                self.dealer_deck.append(card)
        self.update_ui()
        # Settle hands
        if self.split_mode:
            # compare each split hand to dealer
            results = []
            dealer_val = self.get_hand_value(self.dealer_deck)
            for idx, hand in enumerate(self.split_hands):
                user_val = self.get_hand_value(hand)
                bet = self.bets[idx]
                if user_val > 21:
                    # already busted
                    self.balance -= 0  # already accounted
                    results.append((idx, 'lose'))
                elif dealer_val > 21 or user_val > dealer_val:
                    self.balance += bet
                    results.append((idx, 'win'))
                elif user_val < dealer_val:
                    self.balance -= bet
                    results.append((idx, 'lose'))
                else:
                    results.append((idx, 'push'))
            # display simple result
            self.elements.get("result_label") and self.elements["result_label"].destroy()
            res_text = ", ".join([f"Hand {i+1}:{r}" for i, r in results])
            result = Label(self.window, text=res_text, font=(font, 30, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white')
            result.place(x=500, y=75)
            self.elements["result_label"] = result
        else:
            self.check_winner()

    def check_winner(self):
        # Determines the winner and ends the game
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
        # Ends the round, updates balance, and shows result#
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
        # Show play again button
        play_again = Button(self.window, text="Play Again", font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour, fg='white', command=self.play_again)
        play_again.place(x=250, y=50)
        self.elements["play_again"] = play_again

    def play_again(self):
        self.check_bal()
        # Resets the game for another round
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
        # reset split/double state
        self.split_mode = False
        self.split_hands = []
        self.current_hand_idx = 0
        self.bets = []
        self.doubled = False
        self.deal_cards()
        self.update_ui()

    def remove_card_and_total_widgets(self):
        # Remove card widgets (card_slot_*, dealer_slot_*)
        for key in list(self.elements.keys()):
            try:
                if key.startswith("card_slot_") or key.startswith("dealer_slot_"):
                    widget = self.elements.get(key)
                    if widget:
                        try:
                            widget.destroy()
                        except Exception as e:
                            print(f"Failed to destroy widget {key}: {e}")
                    # remove reference from elements dict
                    del self.elements[key]
            except Exception as e:
                print(f"Error removing {key}: {e}")

        # Remove total labels if they exist
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
            # Determine actual username string
            username_value = self.username.get() if hasattr(self.username, 'get') else self.username

            # Delete user from database
            success = delete_user(username_value, self.protecting)
            if not success:
                print("Database error while deleting user")

            # Clear the loaded_user.json file
            try:
                save_json(LOADED_USER_PATH, {})
            except Exception as e:
                print(f"Error clearing loaded_user.json: {e}")

            # FULL window wipe
            for widget in self.window.winfo_children():
                widget.destroy()

                # Return to login screen with deleted account message
            from scenes.login_scene import login
            Login_Scene = login(self.window, self.protecting)
            Login_Scene.acc_deleted()
        else:
            return

    def create_screen(self):
        # Places static UI elements (buttons, labels, static deck)
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
        # Place static deck images vertically at left
        screenheight = self.window.winfo_screenheight()
        start_y = screenheight // 2 - 200
        #for i in range(1, 11):
            #self.elements[f"static_deck_{i}"].place(x=50, y=start_y + (i - 1) * 30)

    def run(self):
        # Starts the game, sets up UI and deals first cards
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
        # Double the bet for the current hand, draw one card, then stand
        if self.split_mode:
            hand = self.split_hands[self.current_hand_idx]
            if len(hand) != 2:
                return
            # double current hand bet if possible
            try:
                if self.balance < self.bets[self.current_hand_idx]:
                    return
            except Exception:
                return
            self.bets[self.current_hand_idx] *= 2
            # draw one card
            card = self.main_deck.deal_card()
            if card:
                hand.append(card)
                self.update_ui()
            # after double, move to next hand or dealer
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
            # double bet
            self.bet *= 2
            card = self.main_deck.deal_card()
            if card:
                self.user_deck.append(card)
                self.update_ui()
            # dealer plays
            self.game_over = True
            self.dealer_play()

    def split_hand(self):
        # Split the player's two-card hand into two hands if ranks match
        if len(self.user_deck) != 2:
            return
        first_card = self.user_deck[0]['name'][0]
        second_card = self.user_deck[1]['name'][0]
        if first_card != second_card:
            return
        # ensure sufficient balance for second bet
        if self.balance < self.bet:
            return
        # create two hands and place equal bets
        self.split_mode = True
        self.split_hands = [[self.user_deck[0]], [self.user_deck[1]]]
        self.bets = [self.bet, self.bet]
        # deduct second bet from balance
        self.balance -= self.bet
        self.current_hand_idx = 0
        self.update_ui()