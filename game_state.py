class World:
    """Represents global game states (time and navigation)."""

    def __init__(self) -> None:
        """Initialize the world with default time and starting location."""
        self.days = 0
        self.time = 408
        self.current_location = 'Start'

    def show_days(self) -> int:
        """Show how many days have passed since the start of game."""
        days = (self.time // 60) // 24
        return days

    def show_time(self) -> str:
        """Show current tme in the game."""
        h = (self.time // 60) % 24
        m = self.time % 60
        return f'{h:02}:{m:02}'


class Hero:
    """Represents the hero and his personal state."""

    def __init__(self):
        """Initialize the hero with default health, hanger, fatigue, cash."""
        self.health = 100
        self.fatigue = 100
        self.hanger = 100
        self.cash = 20


class Truck:
    """Represents the truck and its state."""

    def __init__(self) -> None:
        """Initialize the truck with default truck condition, fuel, space available."""
        self.truck_condition = 100
        self.fuel = 100
        self.truck_space = 10
        self.passenger = False


class GameState:
    """Main container for the game state."""

    def __init__(self) -> None:
        """Initialize the full game state with default world, hero and truck."""
        self.world = World()
        self.hero = Hero()
        self.truck = Truck()
