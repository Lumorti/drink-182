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
import serial

from functools import partial
import copy
import time
import json

fs = 25

maxVol = 350
maxChange = 25
maxBooze = 100

correctCode = "19734628"

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
        ingred["og"] = ingred["ml"]
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

        # Setup serial interface with Arduino
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=3)
        if not self.ser:
            self.ser = serial.Serial('/dev/ttyACM1', 9600, timeout=3)
        print(self.ser.name)
        self.ser.write(b'hello')

        Window.size = (480, 800)
        self.currentDrink = {}
        self.code = ""
        self.menu = 0
        self.settings = {"maxBooze": 100, "maxVol": 350, "maxChange": 25}
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
            startButton.size_hint = 0.5, 0.2
            startButton.font_size = 35
            buttonEvent = partial(self.setMenu, 1)
            startButton.bind(on_press=buttonEvent)
            self.startLayout.add_widget(startButton)

            # Add the settings button
            self.settingsLayout = AnchorLayout(anchor_x='left', anchor_y='bottom')
            self.settingsLayout.size = Window.size
            self.settingsLayout.center = Window.center
            settingsButton = Button(text="")
            settingsButton.size_hint = None, None
            settingsButton.size = 50, 50
            settingsButton.font_size = 15
            buttonEvent = partial(self.setMenu, 3)
            settingsButton.bind(on_press=buttonEvent)
            self.settingsLayout.add_widget(settingsButton)

            # Add the layouts to the main widget
            self.add_widget(self.startLayout)
            self.add_widget(self.settingsLayout)

        elif self.menu == 1:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='center', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1] * 0.95
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/1.1, Window.height/10.0), font_size=fs)
            btn.bind(on_press=partial(self.setMenu, 0))
            self.backLayout.add_widget(btn)
                
            # Set up the centered drinks list
            self.mainLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.mainLayout.size_hint = None, None
            self.mainLayout.size = Window.size[0], Window.size[1]
            self.mainLayout.center = Window.center
            layout = GridLayout(cols=1, spacing=30, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            
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
            scrolling.size = self.mainLayout.size[0]*0.75, self.mainLayout.size[1]*0.83
            scrolling.center = self.mainLayout.center
            scrolling.bar_width = 0
            layout.center = scrolling.center
            self.mainLayout.add_widget(scrolling)

            # Add the various sections to the root widget
            self.add_widget(self.mainLayout)
            self.add_widget(self.backLayout)

        elif self.menu == 2:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='center', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1] * 0.95
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/1.1, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.setMenu, 1)
            btn.bind(on_press=buttonEvent)
            self.backLayout.add_widget(btn)
            
            # Add the make button
            self.makeLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.makeLayout.size_hint = None, None
            self.makeLayout.size = Window.size[0], Window.size[1] * 0.95
            self.makeLayout.center = Window.center
            btn = Button(id="btnmake", text = "make", size_hint=(None, None), size=(Window.width/1.1, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.makeDrink, self.currentDrink)
            btn.bind(on_press=buttonEvent)
            self.makeLayout.add_widget(btn)

            # Make the central layout
            self.drinkLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.drinkLayout.size_hint = None, None
            self.drinkLayout.size = Window.size[0], Window.size[1]
            self.drinkLayout.center = Window.center

            for ing in self.currentDrink["ingredients"]:
                if ing["name"] not in liquidsAvail:
                    print("substituting " + ing["name"] + " for " + getLiquid(ing["name"])["subs"])
                    ing["oldName"] = ing["name"]
                    ing["name"] = getLiquid(ing["name"])["subs"]
            
            # Add the drop down boxes to the info 
            self.drinkInfo = GridLayout(cols=4, spacing=15, size_hint=(None,None))
            for index, ing in enumerate(self.currentDrink["ingredients"]):
                if "oldName" in ing.keys():
                    spinner = Label(text=ing["oldName"]+"\n("+ing["name"]+")", size_hint=(None, None), size=(190, 50), font_size=fs)
                else:
                    spinner = Label(text=ing["name"], size_hint=(None, None), size=(190, 50), font_size=fs)
                spinner.ind = index

                self.drinkInfo.add_widget(spinner)
                btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
                btn.bind(on_press=partial(self.changeDrink, index, -25))
                self.drinkInfo.add_widget(btn)
                lbl = Label(id="lbl"+str(index),text=str(ing["ml"])+" ml", size_hint=(None, None), height=50, width=80, font_size=fs)
                self.drinkInfo.add_widget(lbl)
                btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
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
            self.add_widget(self.drinkLayout)
            self.add_widget(self.makeLayout)

            self.checkDrink()

        elif self.menu == 3:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='center', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1] * 0.95
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/1.1, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.setMenu, 0)
            btn.bind(on_press=buttonEvent)
            self.backLayout.add_widget(btn)
            
            # Create the keypad
            self.keypadWrapper = AnchorLayout(anchor_x='center', anchor_y='center')
            self.keypadWrapper.size_hint = None, None
            self.keypadWrapper.size = Window.size[0], Window.size[1] 
            self.keypadWrapper.center = Window.center
            self.keypadLayout = GridLayout(cols=3)
            self.keypadLayout.size_hint = None, None
            self.keypadLayout.size = Window.size[0]*0.5, Window.size[1]*0.5
            self.keypadLayout.center = Window.center
            for i in range(9):
                btn = Button(size_hint=(None,None), size=(80,80), font_size=fs)
                buttonEvent = partial(self.enterCode, i+1)
                btn.bind(on_press=buttonEvent)
                self.keypadLayout.add_widget(btn)
            self.keypadWrapper.add_widget(self.keypadLayout)

            # Add the various sections to the root widget
            self.add_widget(self.backLayout)
            self.add_widget(self.keypadWrapper)

        elif self.menu == 4:

            # Add the back button
            self.backLayout = AnchorLayout(anchor_x='center', anchor_y='top')
            self.backLayout.size_hint = None, None
            self.backLayout.size = Window.size[0], Window.size[1] * 0.95
            self.backLayout.center = Window.center
            btn = Button(text = "back", size_hint=(None, None), size=(Window.width/1.1, Window.height/10.0), font_size=fs)
            buttonEvent = partial(self.setMenu, 0)
            btn.bind(on_press=buttonEvent)
            self.backLayout.add_widget(btn)

            # Add the back button
            self.controlLayout = AnchorLayout(anchor_x='center', anchor_y='center')
            self.controlLayout.size_hint = None, None
            self.controlLayout.size = Window.size[0], Window.size[1] * 0.95
            self.controlLayout.center = Window.center
            self.controlGrid = GridLayout(cols=4, spacing=15, size_hint=(None,None))
            self.controlGrid.size = (Window.size[0]-30, 50) 

            # Add a value setting
            lbl = Label(text="maxBooze", size_hint=(None, None), height=50, width=180, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxBooze", -25))
            self.controlGrid.add_widget(btn)
            lbl = Label(id="maxBooze",text=str(self.settings["maxBooze"]), size_hint=(None, None), height=50, width=80, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxBooze", 25))
            self.controlGrid.add_widget(btn)

            # Add a value setting
            lbl = Label(text="maxVol", size_hint=(None, None), height=50, width=180, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxVol", -25))
            self.controlGrid.add_widget(btn)
            lbl = Label(id="maxVol",text=str(self.settings["maxVol"]), size_hint=(None, None), height=50, width=80, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxVol", 25))
            self.controlGrid.add_widget(btn)
            
            # Add a value setting
            lbl = Label(text="maxChange", size_hint=(None, None), height=50, width=180, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxChange", -25))
            self.controlGrid.add_widget(btn)
            lbl = Label(id="maxChange",text=str(self.settings["maxChange"]), size_hint=(None, None), height=50, width=80, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "maxChange", 25))
            self.controlGrid.add_widget(btn)
            
            # Add the various sections to the root widget
            self.add_widget(self.backLayout)
            self.controlLayout.add_widget(self.controlGrid)
            self.add_widget(self.controlLayout)

    def enterCode(self, num, *largs):

        if num != 5:
            self.code += str(num)
        else:
            if self.code == correctCode:
                self.setMenu(4)
            print("submitted code: " + self.code)
            self.code = ""

    def setDrink(self, drinkObj, *largs):

        self.currentDrink = copy.deepcopy(drinkObj)
        print("drink is now: " + repr(self.currentDrink))
        self.setMenu(2)

    def makeDrink(self, drinkObj, *largs):

        print("making drink:" + repr(drinkObj))

        sendString = "-"
        for ing in self.currentDrink["ingredients"]:
            motorIndex = 0
            for index, liq in enumerate(liquidsAvail):
                if liq == ing["name"]: 
                    motorIndex = index
                    break
            sendString += str(motorIndex) + "=" + str(int(ing["ml"])) + "+"
        sendString += "-\n"

        if self.ser:
            print("serial availible, sending: " + sendString)
            self.ser.write(bytes(sendString,"utf-8"))
        else:
            print("serial unavailible")

        self.setMenu(0)

    def changeSetting(self, setting, change, *largs):

        self.settings[setting] += change
        for wid in self.controlGrid.children:
            if wid.id == setting:
                wid.text = str(self.settings[setting])

        print("setting " + setting + " is now " + str(self.settings[setting]))

    def changeDrink(self, index, change, *largs):

        print("changing drink ingredient at index:" + str(index) + " by: " + str(change))

        ing = self.currentDrink["ingredients"][index]
        if ing["ml"]+change >= ing["og"] - self.settings["maxChange"] and ing["ml"]+change <= ing["og"] + self.settings["maxChange"]:
            ing["ml"] += change

        if ing["ml"] < 0:
            ing["ml"] = 0

        for wid in self.drinkInfo.children:
            if wid.id == "lbl" + str(index):
                wid.text = str(self.currentDrink["ingredients"][index]["ml"]) + " ml"

        self.checkDrink()

    def checkDrink(self):

        numUnits = 0
        totalVol = 0

        for ingred in self.currentDrink["ingredients"]:
            numUnits += float(getLiquid(ingred["name"])["units"]) * float(ingred["ml"]) / 25.0
            totalVol += float(ingred["ml"])

        percent = 100.0 * float(numUnits) * 25.0 * 0.4 / float(totalVol)

        print("drink has " + str(numUnits) + " units within " + str(totalVol) + " ml")

        # Ensure that the drink is valid
        if numUnits * 25.0 > maxBooze:
            self.makeLayout.children[0].text = "can't make, too boozy"
            self.makeLayout.children[0].disabled = True
        elif totalVol > maxVol:
            self.makeLayout.children[0].text = "can't make, won't fit in cup"
            self.makeLayout.children[0].disabled = True
        else:
            self.makeLayout.children[0].text = "make (" + str(numUnits) + " units, " + str(round(percent, 1)) + "%)"
            self.makeLayout.children[0].disabled = False

class DrinksApp(App):
    def build(self):
        ui = DrinksUI()
        return ui

if __name__ == '__main__':
    DrinksApp().run()
