from tkinter import *
import sys

background_colour = "#416CBC"
asset_colour = '#7d7d7d'
font = 'Terminal'


class BaseScene():
    def __init__(self, window):
        self.window = window
        self.elements = []
        self.background = None
    
    def clear_screen(self):
        for element in self.elements.values():
            try:
                element.place_forget()
            except Exception as e:
                print(f"Element failed to remove {element} {e}")
    
    def load_scene(self):
        background = Label(self.window, bg=background_colour)
        background.place(x=0, y=0, relwidth = 1, relheight=1)

class MenuScene(BaseScene):
    def __init__(self, window):
        self.window = window
        self.elements = {}
        super().load_scene()
        self.load_scene()

    def load_scene(self):
        self.elements["Title_Text"] = Label(self.window, text = "An Average Campaign", font=(font, 40, 'bold'), fg='#ffffff', bg=asset_colour, relief=RAISED, bd=10)
        self.elements["Title_Text"].place(relx=0.5, rely=0.1, anchor=CENTER)
        self.elements["Skill_Tree"] = Button(self.window, text="Skill Tree", font=(font, 40, 'bold'), fg='#ffffff', bg=asset_colour, relief=RAISED, bd=10, command=lambda: self.load_skill_tree())
        self.elements["Skill_Tree"].place(relx = 0.5, rely=0.5, anchor=CENTER)
        self.elements["Quit_Button"] = Button(self.window, text="Quit", font=(font, 40, 'bold'), fg='#ffffff', bg=asset_colour, relief=RAISED, bd=10, command=lambda: sys.exit())
        self.elements["Quit_Button"].place(relx = 0.05, rely=0.9, anchor="w")
    
    def clear_screen(self):
        super().clear_screen()
    
    def load_skill_tree(self):
        self.clear_screen()
        Skill_Tree = SkillTree(self.window)

class SkillTree(BaseScene):
    def __init__(self, window):
        self.window = window
        self.elements = {}
        super().load_scene()
        self.load_scene()
    
    def load_scene(self):
        self.elements["Title_Text"] = Label(self.window, text = "Skill Tree", font=(font, 40, 'bold'), fg='#ffffff', bg=asset_colour, relief=RAISED, bd=10)
        self.elements["Title_Text"].place(relx=0.5, rely=0.1, anchor=CENTER)
        self.elements["Back_Button"] = Button(self.window, text="Back", font=(font, 40, 'bold'), fg='#ffffff', bg=asset_colour, relief=RAISED, bd=10, command=lambda: self.back())
        self.elements["Back_Button"].place(relx=0.05, rely=0.9, anchor="w")

    def back(self):
        super().clear_screen()
        Main_Scene = MenuScene(self.window)

class Entity():
    def __init__(self):
        pass

class Player(Entity):
    def __init__(self):
        self.health = 100
        self.points = 10
        self.INT = 0
        self.STR = 0
    
    def inc_INT(self):
        self.INT += 1
        self.points -= 1
    
    def inc_STR(self):
        self.STR += 1
        self.points -= 1
    
    def display_stats(self):
        print(self.health)
        print(self.points)
        print(self.INT)
        print(self.STR)










class Main:
    def __init__(self):
        self.window = None
        self.canvas = None
    
    def run(self):
        self.window = Tk()
        self.window.geometry("1280x720")
        self.canvas = Canvas(self.window, width=1920, height=1080)

        Main_Scene = MenuScene(self.window)
        Player1 = Player()
        Player1.inc_INT()
        Player1.inc_INT()
        Player1.inc_INT()
        Player1.inc_STR()
        Player1.inc_STR()
        Player1.display_stats()
        # Main_Scene.load_scene()

        self.canvas.place(x=0, y=0)
        self.window.mainloop()

if __name__ == "__main__":
    Main_Class = Main()
    Main_Class.run()