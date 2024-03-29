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
import sys
import glob
import serial
import os

os.environ['KIVY_WINDOW'] = 'egl_rpi'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

fs = 25

# correctCode = ""
correctCode = "19734628"

Builder.load_string("""

<SpinnerOption>:
    size_hint: None, None
    size: 200, 60,
    font_size: 25

""")

with open("liquids.json") as f:
    liquidList = json.load(f)["data"]

liquidNameList = []
for l in liquidList:
    liquidNameList.append(l["name"])

with open("drinks.json") as f:
    drinksList = json.load(f)["data"]

print("loaded " + str(len(liquidList)) + " liquids")
print("loaded " + str(len(drinksList)) + " drinks")

Config.set('graphics', 'fullscreen', 'borderless')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '0')
Config.set('graphics', 'maxfps', '10')

# Return the liquid object from a name
def getLiquid(name):
    for l in liquidList:
        if l["name"] == name: return l
    return None

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class DrinksUI(Widget):

    def __init__(self, **kwargs):
        super(DrinksUI, self).__init__(**kwargs)

        # Setup serial interface with Arduino
        try:
            self.ser = serial.Serial(serial_ports()[0], 9600, timeout=3)
            print("connected on port: " + self.ser.name)
        except: 
            self.ser = None

        Window.size = (480, 800)

        self.currentDrink = {}
        self.code = ""
        self.menu = 0

        # Load the settings from file
        with open("settings.json") as f:
            self.settings = json.load(f)
            print("loaded the following from settings file:")
            print(self.settings)

        self.update_drinks_list()
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
            layout.size_hint_x = 0.8
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
            scrolling.bar_width = 30
            scrolling.bar_margin = 0
            scrolling.bar_inactive_color = [.7,.7,.7,.9]
            scrolling.scroll_type = ["bars"]
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
            buttonEvent = partial(self.makeDrink)
            btn.bind(on_press=buttonEvent)
            self.makeLayout.add_widget(btn)

            # Make the central layout
            self.drinkLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.drinkLayout.size_hint = None, None
            self.drinkLayout.size = Window.size[0], Window.size[1]
            self.drinkLayout.center = Window.center

            for ing in self.currentDrink["ingredients"]:
                if ing["name"] not in self.settings["liquidsAvail"]:
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

            self.controlLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.controlLayout.size_hint = None, None
            self.controlLayout.size = Window.size[0]*0.9, Window.size[1] * 0.80
            self.controlLayout.center = (Window.center[0], Window.center[1]-50)

            # Set up the wrapper grid
            self.wrapperGrid = GridLayout(cols=1, spacing=15, size_hint=(None,None))
            self.wrapperGrid.size = (self.controlLayout.size[0]*0.99, self.controlLayout.size[1]*0.99) 
            self.wrapperGrid.center = self.controlLayout.center

            # Set up the liquid list grid
            self.liquidGrid = GridLayout(cols=2, spacing=15, size_hint=(None,None))
            self.liquidGrid.size = (self.wrapperGrid.size[0]*0.9, self.wrapperGrid.size[1] * 0.5) 
            self.liquidGrid.center = (self.wrapperGrid.center[0],self.wrapperGrid.center[1])
            for index, liq in enumerate(self.settings["liquidsAvail"]):
                spinner = Spinner(
                    text=liq,
                    id="sd"+str(index),
                    values=liquidNameList,
                    size_hint=(None, None),
                    size=(200, 60),
                    font_size=fs,
                    pos_hint=(None,None))
                spinner.bind(text=self.change_avail_drink)
                self.liquidGrid.add_widget(spinner)

            # Add the settings layout
            self.controlGrid = GridLayout(cols=4, spacing=15, size_hint=(None,None))
            self.controlGrid.size = (self.wrapperGrid.size[0]*0.9, self.wrapperGrid.size[1] * 0.30) 
            self.controlGrid.center = self.wrapperGrid.center

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
            
            # Add buttons to change active solenoid setting 
            lbl = Label(text="selectedDrink", size_hint=(None, None), height=50, width=180, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "selectedSetting", -1))
            self.controlGrid.add_widget(btn)
            lbl = Label(id="selectedSetting",text=str(self.settings["selectedSetting"]), size_hint=(None, None), height=50, width=80, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "selectedSetting", 1))
            self.controlGrid.add_widget(btn)

            # Add a value setting
            lbl = Label(text="milliPer25", size_hint=(None, None), height=50, width=180, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="-", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "milliPer25", -5, self.settings["selectedSetting"]))
            self.controlGrid.add_widget(btn)
            lbl = Label(id="milliPer25",text=str(self.settings["milliPer25"][self.settings["selectedSetting"]-1]), size_hint=(None, None), height=50, width=80, font_size=fs)
            self.controlGrid.add_widget(lbl)
            btn = Button(text="+", size_hint=(None, None), height=50, width=50, font_size=fs)
            btn.bind(on_press=partial(self.changeSetting, "milliPer25", 5))
            self.controlGrid.add_widget(btn)

            # Add the various sections to the root widget
            self.add_widget(self.backLayout)
            self.wrapperGrid.add_widget(self.liquidGrid)
            self.wrapperGrid.add_widget(self.controlGrid)
            self.controlLayout.add_widget(self.wrapperGrid)
            self.add_widget(self.controlLayout)

    def update_drinks_list(self, *largs):

        # Determine which drinks are now availible
        for drink in drinksList:
            canMake = True
            for ingred in drink["ingredients"]:
                ingred["og"] = ingred["ml"]
                liq = getLiquid(ingred["name"])
                if liq:
                    if liq["name"] not in self.settings["liquidsAvail"] and liq["subs"] not in self.settings["liquidsAvail"]:
                        canMake = False
                        break
                else:
                    print("unknown liquid: " + str(ingred["name"]))
                    canMake = False
                    break
            drink["canMake"] = canMake

    def change_avail_drink(self, spinner, text, *largs):

        global drinksList

        ind = int(spinner.id[2:])
        print ("changing availible liquid at index " + str(ind) + " to " + text)
        self.settings["liquidsAvail"][ind] = text
        self.update_drinks_list()

        with open("settings.json", "w") as f:
            json.dump(self.settings, f)

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

    def makeDrink(self, *largs):

        print("making drink:" + repr(self.currentDrink))

        # Move this to the top of the list
        for k, drink in enumerate(drinksList):
            if drink["name"] == self.currentDrink["name"]:
                drinksList.insert(0, drinksList.pop(k))
                break

        # Generate the string to send to the Arduino
        sendString = "-"
        for ing in self.currentDrink["ingredients"]:
            motorIndex = 0
            for index, liq in enumerate(self.settings["liquidsAvail"]):
                if liq == ing["name"]: 
                    motorIndex = index
                    break
            sendString += str(motorIndex) + "=" + str(int(self.settings["milliPer25"][motorIndex]*(ing["ml"]/25))) + "+"
        sendString += "-\n"

        if self.ser:
            print("serial available, sending: " + sendString)
            self.ser.flushOutput()
            time.sleep(0.1)
            self.ser.write(bytes(sendString,"utf-8"))
        else:
            print("serial unavailable, would've sent: " + sendString)

        self.setMenu(0)

    def changeSetting(self, setting, change, selectedIndex=-1,*largs):

        if setting != "milliPer25":

            self.settings[setting] += change

            if setting == "selectedSetting" and (self.settings[setting] > 8 or self.settings[setting] < 1):
                self.settings[setting] -= change

            for wid in self.controlGrid.children:
                if wid.id == setting:
                    wid.text = str(self.settings[setting])
                elif setting == "selectedSetting" and wid.id == "milliPer25":
                    wid.text = str(self.settings["milliPer25"][self.settings[setting]-1])

        else:

            self.settings[setting][self.settings["selectedSetting"]-1] += change

            for wid in self.controlGrid.children:
                if wid.id == setting:
                    wid.text = str(self.settings[setting][self.settings["selectedSetting"]-1])

        with open("settings.json", "w") as f:
            json.dump(self.settings, f)

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
        if numUnits * 25.0 > self.settings["maxBooze"]:
            self.makeLayout.children[0].text = "can't make, too boozy"
            self.makeLayout.children[0].disabled = True
        elif totalVol > self.settings["maxVol"] and not "debug" in self.currentDrink["name"]:
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
