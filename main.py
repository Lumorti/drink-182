#!/usr/bin/python3
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from functools import partial

menu = 0

liquidList = []
drinksList = []

liquidList.append({"name": "vodka", "units": 1, "color":"white"})
liquidList.append({"name": "lemonade", "units": 0, "color":"yellow"})
liquidList.append({"name": "coke", "units": 0, "color":"black"})
liquidList.append({"name": "orange", "units": 0, "color":"orange"})

drinksList.append({"name": "vodka lemonade", "ingredients": [{"name": "vodka", "ml": 50}, {"name": "lemonade", "ml": 200}]})
drinksList.append({"name": "vodka coke", "ingredients": [{"name": "vodka", "ml": 50}, {"name": "coke", "ml": 200}]})

class DrinksUI(Widget):

    def __init__(self, **kwargs):
        super(DrinksUI, self).__init__(**kwargs)

        self.startLayout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.startLayout.size = Window.size
        self.startLayout.center = Window.center

        startButton = Button(text="Start")
        startButton.size_hint = 0.5, 0.3
        startButton.font_size = 40
        buttonEvent = partial(self.setMenu, 1)
        startButton.bind(on_press=buttonEvent)

        self.startLayout.add_widget(startButton)
        self.add_widget(self.startLayout)

    def setMenu(self, menuNum, *largs):

        menu = menuNum
        print("menu is now: " + str(menuNum))

        if menu == 1:

            self.remove_widget(self.startLayout)

            self.mainLayout = AnchorLayout(anchor_x='center', anchor_y='bottom')
            self.mainLayout.size_hint = None, None
            self.mainLayout.size = Window.size[0], Window.size[1]
            self.mainLayout.center = Window.center

            layout = GridLayout(cols=1, spacing=30, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))

            for i in range(100):
                btn = Button(text = str(drinksList[1]["name"]))
                btn.font_size = 25
                btn.size_hint_y = None 
                btn.height = 60
                layout.add_widget(btn)

            scrolling = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
            scrolling.add_widget(layout)
            scrolling.size_hint = None, None
            scrolling.size = self.mainLayout.size[0]*0.55, self.mainLayout.size[1]*0.75
            scrolling.center = self.mainLayout.center
            layout.center = scrolling.center
            self.mainLayout.add_widget(scrolling)
            self.add_widget(self.mainLayout)

            # TODO add title (top)
            # TODO add back button (top left)
            # TODO add settings button (bottom left)
            # TODO add add drink button (bottom right)

        pass

    pass

class DrinksApp(App):
    def build(self):
        ui = DrinksUI()
        return ui

if __name__ == '__main__':
    DrinksApp().run()
