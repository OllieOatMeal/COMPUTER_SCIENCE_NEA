from tkinter import *
import random as r
import sqlite3
from variables import *

# Represents a single playing card
class Card:
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
    def __init__(self, window, username, balance):
        self.window = window
        self.username = username
        self.balance = balance
        self.elements = {}         # Stores all UI elements
        self.background = None
        self.main_deck = None

        self.user_deck = []        # Player's hand
        self.dealer_deck = []      # Dealer's hand

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
            self.window.configure(bg='#1803A5')  # fallback background color

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


    def save_and_exit(self):
        # Saves balance and games played to the database, then returns to main menu
        connection = sqlite3.connect(database_path)
        cusor = connection.cursor()
        cusor.execute(
            "SELECT GamesPlayed FROM Users WHERE UserName = ?", (self.username.get(),)
        )
        games_played = cusor.fetchone()
        games_played = games_played[0] if games_played else 0
        games_played += 1
        connection.close()
        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE Users SET Money = ?, GamesPlayed = ? WHERE UserName = (?)",
                (self.balance, games_played, self.username.get(),)
            )
            connection.commit()
            connection.close()
        except sqlite3.Error as e:
            print(f"Database error while saving money: {e}")
        finally:
            from scenes.main_menu import main_menu
            self.clear_screen()  # Clear current game UI
            Main_Menu = main_menu(self.window, self.username)
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

        start_card_x = 50
        start_count_x = 50
        y_player_card = 650
        y_dealer_card = 300
        y_player_count = 600
        y_dealer_count = 250
        spacing = 80

        # Player cards
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

        # Player total label
        player_total = self.get_hand_value(self.user_deck)
        self.elements["player_total_label"] = Label(
            self.window, text=f"Player Total: {player_total}", font=(font, 20, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='white'
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
            self.user_deck.append(card)
            self.update_ui()
            if self.get_hand_value(self.user_deck) > 21:
                self.end_game("Bust! Dealer wins.")

    def stand(self):
        # Player stands, dealer draws until 17 or higher
        if self.game_over:
            return
        while self.get_hand_value(self.dealer_deck) < 17:
            card = self.main_deck.deal_card()
            if card:
                self.dealer_deck.append(card)
        self.update_ui()
        self.check_winner()

    def check_winner(self):
        # Determines the winner and ends the game
        user_val = self.get_hand_value(self.user_deck)
        dealer_val = self.get_hand_value(self.dealer_deck)
        if dealer_val > 21 or user_val > dealer_val:
            self.end_game("You win!", win=True)
        elif user_val < dealer_val:
            self.end_game("Dealer wins.")
        else:
            self.end_game("Push (Draw).")

    def end_game(self, message, win=False):
        # Ends the round, updates balance, and shows result
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

            # Delete user
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM Users WHERE UserName = ?", (self.username.get(),)
            )
            connection.commit()
            connection.close()

            # FULL window wipe (fixes your issue)
            for widget in self.window.winfo_children():
                widget.destroy()

            # Load main menu
            from scenes.main_menu import main_menu
            Main_Menu = main_menu(self.window, self.username)
            Main_Menu.logout()
        else:
            pass

    def create_screen(self):
        # Places static UI elements (buttons, labels, static deck)
        self.elements["exit_button"].place(x=50, y=50)
        if "balance_label" in self.elements:
            self.elements["balance_label"].place(x=50, y=1000)
        if "hit_button" in self.elements:
            self.elements["hit_button"].place(x=900, y=1000)
        if "stand_button" in self.elements:
            self.elements["stand_button"].place(x=1000, y=1000)
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