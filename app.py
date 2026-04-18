from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window  # Required for keyboard
from kivy.storage.jsonstore import JsonStore
import random

GRID_SIZE = 25 

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = [[10, 10], [10, 9], [10, 8], [10, 7]]
        self.direction = Vector(0, 1) 
        self.score = 0
        self.food = [random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)]
        
        # Initialize Keyboard
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.score_label = Label(text=f"Score: {self.score}", pos_hint={'top': 1}, size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.add_widget(self.score_label)
        self.game_clock = None

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Prevent 180-degree turns: if current is UP, can't press DOWN
        new_dir = self.direction
        
        if keycode[1] == 'up':
            new_dir = Vector(0, 1)
        elif keycode[1] == 'down':
            new_dir = Vector(0, -1)
        elif keycode[1] == 'left':
            new_dir = Vector(-1, 0)
        elif keycode[1] == 'right':
            new_dir = Vector(1, 0)

        if new_dir + self.direction != Vector(0, 0):
            self.direction = new_dir
        return True

    def update(self, dt):
        new_head = [self.snake[0][0] + self.direction.x, self.snake[0][1] + self.direction.y]

        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or 
            new_head[1] < 0 or new_head[1] >= GRID_SIZE or 
            new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.score_label.text = f"Score: {self.score}"
            self.food = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        else:
            self.snake.pop()

        self.draw_game()

    def game_over(self):
        if self.game_clock:
            self.game_clock.cancel()
        app = App.get_running_app()
        app.sm.current = 'end'
        app.end_screen.update_scores(self.score)

    def reset_game(self):
        self.snake = [[10, 10], [10, 9], [10, 8], [10, 7]]
        self.direction = Vector(0, 1)
        self.score = 0
        self.score_label.text = f"Score: {self.score}"
        self.food = [random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)]
        if self.game_clock:
            self.game_clock.cancel()
        self.game_clock = Clock.schedule_interval(self.update, 1.0 / 10.0)
        self.draw_game()

    def draw_game(self):
        self.canvas.clear()
        cw = self.width / GRID_SIZE
        ch = self.height / GRID_SIZE
        with self.canvas:
            Color(0.05, 0.05, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(1, 0.2, 0.2, 1)
            Ellipse(pos=(self.food[0]*cw, self.food[1]*ch), size=(cw, ch))
            Color(0.2, 0.8, 0.2, 1)
            for part in self.snake:
                Rectangle(pos=(part[0]*cw + 1, part[1]*ch + 1), size=(cw-2, ch-2))

# --- Screens remain mostly the same, ensuring high_score exists ---

class SnakeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        title = Label(text="Snake Game", font_size=48)
        self.high_score_label = Label(text="High Score: 0", font_size=24)
        start_button = Button(text="Start Game", font_size=32, size_hint=(1, 0.3))
        start_button.bind(on_press=self.start_game)
        btn_home = Button(text="Home", size_hint=(1, 0.3))
        btn_home.bind(on_press=self.go_to_home)
        layout.add_widget(title)
        layout.add_widget(self.high_score_label)
        layout.add_widget(start_button)
        layout.add_widget(btn_home)
        self.add_widget(layout)
    
    def start_game(self, instance):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.game.reset_game()

    def go_to_home(self, instance):
        app = App.get_running_app()
        app.sm.current = 'home'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = SnakeGame()
        self.add_widget(self.game)

class EndScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.score_label = Label(text="", font_size=32)
        self.high_score_label = Label(text="", font_size=24)
        btn_restart = Button(text="Restart", size_hint=(1, 0.3))
        btn_restart.bind(on_press=self.restart_game)
        btn_home = Button(text="Home", size_hint=(1, 0.3))
        btn_home.bind(on_press=self.go_to_home)
        layout.add_widget(self.score_label)
        layout.add_widget(self.high_score_label)
        layout.add_widget(btn_restart)
        layout.add_widget(btn_home)
        self.add_widget(layout)
    
    def update_scores(self, score):
        app = App.get_running_app()
        self.score_label.text = f"Score: {score}"
        if score > app.high_score:
            app.high_score = score
            app.store.put('high_score', value=app.high_score)
        self.high_score_label.text = f"High Score: {app.high_score}"

    def restart_game(self, instance):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.game.reset_game()

    def go_to_home(self, instance):
        app = App.get_running_app()
        app.sm.current = 'home'


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        title = Label(text="Home Screen", font_size=48)
        btn_go_snake = Button(text="Go to Snake Game", font_size=32, size_hint=(1, 0.3))
        btn_go_snake.bind(on_press=self.go_to_snake)
        
        layout.add_widget(title)
        layout.add_widget(btn_go_snake)
        self.add_widget(layout)

    def go_to_snake(self, instance):
        app = App.get_running_app()
        app.sm.current = 'snake'
        app.snake_screen.high_score_label.text = f"High Score: {app.high_score}"

class SnakeApp(App):
    def build(self):
        self.store = JsonStore('snake_high_score.json')
        self.high_score = self.store.get('high_score')['value'] if self.store.exists('high_score') else 0
        self.sm = ScreenManager()
        self.home_screen = HomeScreen(name='home')
        self.snake_screen = SnakeScreen(name='snake')
        self.game_screen = GameScreen(name='game')
        self.end_screen = EndScreen(name='end')
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.snake_screen)
        self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.end_screen)
        self.snake_screen.high_score_label.text = f"High Score: {self.high_score}"
        return self.sm

if __name__ == '__main__':
    SnakeApp().run()