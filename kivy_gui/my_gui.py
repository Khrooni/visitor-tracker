import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)

        # Set columns
        self.cols = 2

        # Add widgets
        self.add_widget(Label(text="Name: "))
        # Add input Box
        self.name = TextInput(multiline=False)
        self.add_widget(self.name)

        self.add_widget(Label(text="Favorite pizza: "))
        # Add input Box
        self.pizza = TextInput(multiline=False)
        self.add_widget(self.pizza)

        self.add_widget(Label(text="Favorite color: "))
        # Add input Box
        self.color = TextInput(multiline=False)
        self.add_widget(self.color)

        # Create a Submit Button
        self.submit= Button(text="Submit", font_size=32)
        # Bind the button
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)
        
    def press(self, instance):
        name = self.name.text
        pizza = self.pizza.text
        color = self.color.text

        self.add_widget(Label(text=f"My name is {name}. I like {pizza}. My fav color is {color}."))

        self.pizza.text = ""

        print(f"My name is {name}.")
        print(f"I like {pizza}.")
        print(f"My fav color is {color}.")


class MyApp(App):
    def build(self):
        return MyGridLayout()
    
if __name__ == "__main__":
    MyApp().run()
