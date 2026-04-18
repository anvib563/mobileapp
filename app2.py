from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
import random
#kivy application in order for it to work and procress the game

# Game Settings
GRID_SIZE = 25  # Grid adapts to screen size

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = [[10, 10], [10, 9], [10, 8], [10, 7]]
        self.direction = Vector(0, 1)  # Moving UP
        self.score = 0
        self.food = [random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)]
        self.speed = 0.15  # Seconds per frame

        # Touch handling for swipes
        self.touch_start = Vector(0, 0)

        # Score label
        self.score_label = Label(text=f"Score: {self.score}", pos_hint={'top': 1}, size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.add_widget(self.score_label)

        # Game loop (10 FPS)
        self.game_clock = Clock.schedule_interval(self.update, 1.0 / 10.0)

    def on_touch_down(self, touch):
        self.touch_start = Vector(touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        # Calculate Swipe
        swipe = Vector(touch.x, touch.y) - self.touch_start
        if swipe.length() > 30:  # Threshold for swipe
            new_dir = self.direction
            if abs(swipe.x) > abs(swipe.y):
                new_dir = Vector(1, 0) if swipe.x > 0 else Vector(-1, 0)
            else:
                new_dir = Vector(0, 1) if swipe.y > 0 else Vector(0, -1)
            
            # Prevent 180-degree turns
            if new_dir + self.direction != Vector(0, 0):
                self.direction = new_dir

    def update(self, dt):
        # Move Head
        new_head = [self.snake[0][0] + self.direction.x, self.snake[0][1] + self.direction.y]

        # Wall/Self Collision
        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or 
            new_head[1] < 0 or new_head[1] >= GRID_SIZE or 
            new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # Fruit Eating
        if new_head == self.food:
            self.score += 10
            self.score_label.text = f"Score: {self.score}"
            self.food = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        else:
            self.snake.pop()

        self.draw_game()

    def game_over(self):
        self.game_clock.cancel()
        # Transition to end screen
        app = App.get_running_app()
        app.sm.current = 'end'
        app.end_screen.update_scores(self.score)

    def reset_game(self):
        self.snake = [[10, 10], [10, 9], [10, 8], [10, 7]]
        self.direction = Vector(0, 1)
        self.score = 0
        self.score_label.text = f"Score: {self.score}"
        self.food = [random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)]
        self.game_clock = Clock.schedule_interval(self.update, 1.0 / 10.0)
        self.draw_game()

    def draw_game(self):
        self.canvas.clear()
        cw = self.width / GRID_SIZE
        ch = self.height / GRID_SIZE

        with self.canvas:
            # Background
            Color(0.05, 0.05, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Draw Fruit (Red)
            Color(1, 0.2, 0.2, 1)
            Ellipse(pos=(self.food[0]*cw, self.food[1]*ch), size=(cw, ch))

            # Draw Snake (Green)
            Color(0.2, 0.8, 0.2, 1)
            for part in self.snake:
                Rectangle(pos=(part[0]*cw + 1, part[1]*ch + 1), size=(cw-2, ch-2))

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text="Snake Game", font_size=48, color=(1, 1, 1, 1))
        self.high_score_label = Label(text=f"High Score: {App.get_running_app().high_score}", font_size=24, color=(1, 1, 1, 1))
        
        start_button = Button(text="Start Game", font_size=32, size_hint=(1, 0.3))
        start_button.bind(on_press=self.start_game)
        
        layout.add_widget(title)
        layout.add_widget(self.high_score_label)
        layout.add_widget(start_button)
        
        self.add_widget(layout)
        
        with self.canvas:
            Color(0.1, 0.1, 0.3, 1)
            Rectangle(pos=self.pos, size=self.size)
    
    def start_game(self, instance):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.game.reset_game() #default reset in order to work

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = SnakeGame()
        self.add_widget(self.game)

class EndScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        self.game_over_label = Label(text="Game Over", font_size=48, color=(1, 0, 0, 1))
        self.score_label = Label(text="", font_size=32, color=(1, 1, 1, 1))
        self.high_score_label = Label(text="", font_size=24, color=(1, 1, 1, 1))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.3))
        restart_button = Button(text="Restart", font_size=24)
        restart_button.bind(on_press=self.restart_game)
        home_button = Button(text="Home", font_size=24)
        home_button.bind(on_press=self.go_home)
        
        button_layout.add_widget(restart_button)
        button_layout.add_widget(home_button)
        
        self.layout.add_widget(self.game_over_label)
        self.layout.add_widget(self.score_label)
        self.layout.add_widget(self.high_score_label)
        self.layout.add_widget(button_layout)
        
        self.add_widget(self.layout)
        
        with self.canvas:
            Color(0.1, 0.1, 0.3, 1)
            Rectangle(pos=self.pos, size=self.size)
    
    def update_scores(self, score):
        app = App.get_running_app()
        self.score_label.text = f"Score: {score}"
        if score > app.high_score:
            app.high_score = score
            app.store.put('high_score', value=app.high_score)
        self.high_score_label.text = f"High Score: {app.high_score}"
        app.sm.get_screen('home').high_score_label.text = f"High Score: {app.high_score}"
    
    def restart_game(self, instance):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.game.reset_game()
    
    def go_home(self, instance):
        app = App.get_running_app()
        app.sm.current = 'home'

class SnakeApp(App):
    def build(self):
        self.store = JsonStore('snake_high_score.json')
        self.high_score = self.store.get('high_score')['value'] if self.store.exists('high_score') else 0
        
        self.sm = ScreenManager()
        self.home_screen = HomeScreen(name='home')
        self.game_screen = GameScreen(name='game')
        self.end_screen = EndScreen(name='end')
        
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.end_screen)
        
        return self.sm

if __name__ == '__main__':
    SnakeApp().run()
