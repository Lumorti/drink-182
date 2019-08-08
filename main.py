#!/usr/bin/python3
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.config import Config
from kivy.uix.spinner import Spinner
from kivy.lang import Builder

from functools import partial
import copy
import json

fs = 25

Builder.load_string('''
<SpinnerOption>:
    font_size: 25
    size: (190, 70)

''')

with open("liquids.json") as f:
    liquidList = json.load(f)["data"]
liquidNameList = []
for l in liquidList:
    liquidNameList.append(l["name"])
with open("drinks.json") as f:
    drinksList = json.load(f)["data"]

print("loaded " + str(len(liquidList)) + " liquids")
print("loaded " + str(len(drinksList)) + " drinks")

liquidsAvail = ["lemonade", "vodka", "cola", "rum", "tropicalade", "gin", "orangeade", "limeade"]

# Return the liquid object from a name
def getLiquid(name):
    for l in liquidList:
        if l["name"] == name: return l
    return None

# Determine which drinks are availible
for drink in drinksList:
    canMake = True
    for ingred in drink["ingredients"]:
        liq = getLiquid(ingred["name"])
        if liq:
            if liq["name"] not in liquidsAvail and liq["subs"] not in liquidsAvail:
                canMake = False
                break
        else:
            print("unknown liquid: " + str(ingred["name"]))
            canMake = False
            break
    drink["canMake"] = canMake

class DrinksUI(Widget):

    def __init__(self, **kwargs):
        super(DrinksUI, self).__init__(**kwargs)

        Window.size = (480, 800)
        self.currentDrink = {}
        self.menu = 0
        self.setMenu(0)

    def setMenu(self, menuNum, *largs):

        self.menu = menuNum
        print("menu is now: " + str(menuNum))

        # Undo the previous menu
        self.clear_widgets()

        if self.menu == 0:

            # Add the start button
            self.startLayout = AnchorLayout(anchor_x='center', anchor_y='center')
            self.startLayout.size = Window.size
            self.startLayout.center = Window.center
            startButton = Button(text="Start")
            startButton.size_hint = 0.5, 0.3
            startButton.font_size = 40
            buttonEvent = partial(self.setMenu, 1)
            startButton.bind(on_press=buttonEvent)
            self.startLayout.add_widget(startButton)

            # Add the layouts to the main widget
            self.add_widget(self.startLayout)

        elif self.menu == 1:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='left', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1]
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/2.0, Window.height/10.0), font_size=fs)
            btn.bind(on_press=partial(self.setMenu, 0))
            self.backLayout.add_widget(btn)
                
            # Set up the centered drinks list
            self.mainLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.mainLayout.size_hint = None, None
            self.mainLayout.size = Window.size[0], Window.size[1]
            self.mainLayout.center = Window.center
            layout = GridLayout(cols=1, spacing=30, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            
            # Add the custom button
            self.customLayout = AnchorLayout(anchor_x='right', anchor_y='top')
            self.customLayout.size_hint = None, None
            self.customLayout.size = Window.size[0], Window.size[1]
            self.customLayout.center = Window.center
            btn = Button(text = "custom", size_hint=(None,None), size=(Window.width/2.0, Window.height/10.0), font_size=fs)
            btn.bind(on_press=partial(self.setDrink, {"name":"custom", "ingredients":[{"name":"vodka","ml":25}]}))
            self.customLayout.add_widget(btn)

            # Add all the different drinks
            for i in range(len(drinksList)):
                if drinksList[i]["canMake"]:
                    btn = Button(text = str(drinksList[i]["name"]))
                    btn.font_size = 25
                    btn.size_hint_y = None 
                    btn.height = 60
                    btn.bind(on_press=partial(self.setDrink, drinksList[i]))
                    layout.add_widget(btn)
                    
            # Add some spacing at the end
            lbl = Label(text="", height=60)
            layout.add_widget(lbl)

            # Set up scrolling of the main list
            scrolling = ScrollView(size_hint=(None, None), size=(Window.width, Window.height))
            scrolling.add_widget(layout)
            scrolling.size_hint = None, None
            scrolling.size = self.mainLayout.size[0]*0.75, self.mainLayout.size[1]*0.85
            scrolling.center = self.mainLayout.center
            scrolling.bar_width = 0
            layout.center = scrolling.center
            self.mainLayout.add_widget(scrolling)

            # Add the various sections to the root widget
            self.add_widget(self.mainLayout)
            self.add_widget(self.backLayout)
            self.add_widget(self.customLayout)

        elif self.menu == 2:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='left', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1]
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/2.0, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.setMenu, 1)
            btn.bind(on_press=buttonEvent)
            self.backLayout.add_widget(btn)
            
            # Add the make button
            self.makeLayout = AnchorLayout(anchor_x='right', anchor_y='top')
            self.makeLayout.size_hint = None, None
            self.makeLayout.size = Window.size[0], Window.size[1]
            self.makeLayout.center = Window.center
            btn = Button(text = "make", size_hint=(None, None), size=(Window.width/2.0, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.makeDrink, self.currentDrink)
            btn.bind(on_press=buttonEvent)
            self.makeLayout.add_widget(btn)

            # Make the central layout
            self.drinkLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.drinkLayout.size_hint = None, None
            self.drinkLayout.size = Window.size[0], Window.size[1]
            self.drinkLayout.center = Window.center

            # Add the drop down boxes to the info TODO make all boxes work
            self.dropButtons = []
            self.drinkInfo = GridLayout(cols=4, spacing=15, size_hint=(None,None))
            for index, ing in enumerate(self.currentDrink["ingredients"]):
                spinner = Spinner(text=ing["name"], values=liquidNameList, size_hint=(None, None), size=(190, 80), font_size=fs)
                spinner.ind = index
                def show_selected_value(spinner, text):
                    print('The spinner', spinner.ind, 'has text', text)
                    self.currentDrink["ingredients"][spinner.ind]["name"] = text
                spinner.bind(text=show_selected_value)

                self.drinkInfo.add_widget(spinner)
                btn = Button(text="-", size_hint=(None, None), height=80, width=50, font_size=fs)
                btn.bind(on_press=partial(self.changeDrink, index, -25))
                self.drinkInfo.add_widget(btn)
                lbl = Label(id="lbl"+str(index),text=str(ing["ml"])+" ml", size_hint=(None, None), height=80, width=80, font_size=fs)
                self.drinkInfo.add_widget(lbl)
                btn = Button(text="+", size_hint=(None, None), height=80, width=50, font_size=fs)
                btn.bind(on_press=partial(self.changeDrink, index, 25))
                self.drinkInfo.add_widget(btn)

            # Set up the scrolling list of ingredients
            self.scrollingDrinks = ScrollView(size_hint=(None, None), size=(Window.width, Window.height))
            self.scrollingDrinks.size_hint = None, None
            self.scrollingDrinks.size = self.drinkLayout.size[0]*0.85, self.drinkLayout.size[1]*0.85
            self.scrollingDrinks.center = self.drinkLayout.center
            self.scrollingDrinks.add_widget(self.drinkInfo)
            self.drinkLayout.add_widget(self.scrollingDrinks)

            # Add the various sections to the root widget
            self.add_widget(self.backLayout)
            self.add_widget(self.makeLayout)
            self.add_widget(self.drinkLayout)

    def setDrink(self, drinkObj, *largs):

        self.currentDrink = copy.deepcopy(drinkObj)
        print("drink is now: " + repr(self.currentDrink))
        self.setMenu(2)

    def makeDrink(self, drinkObj, *largs):

        print("making drink:" + repr(drinkObj))
        # TODO check to make sure drink is valid

    def changeDrink(self, index, change, *largs):

        print("changing drink ingredient at index:" + str(index) + " by: " + str(change))
        self.currentDrink["ingredients"][index]["ml"] += change

        for wid in self.drinkInfo.children:
            if wid.id == "lbl" + str(index):
                wid.text = str(self.currentDrink["ingredients"][index]["ml"]) + " ml"

        # TODO output info about drink (units/subs)

class DrinksApp(App):
    def build(self):
        ui = DrinksUI()
        return ui

if __name__ == '__main__':
    DrinksApp().run()
