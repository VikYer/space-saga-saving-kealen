class World:
    """Represents global game states (current_time and navigation)."""

    def __init__(self) -> None:
        """Initialize the world with default current_time and starting location."""
        self.days = 0
        self.current_time = 408
        self.current_location = 'Start'
        self.corn_farm = self.CornFarm()
        self.gruber_gas_station = self.GruberGasStation()
        self.biker_mood = None  # ('Biker looks determined', 'Biker is confident', 'Biker is careful', 'Biker is afraid', 'Biker is afraid')

    def show_days(self) -> int:
        """Show how many days have passed since the start of game."""
        days = (self.current_time // 60) // 24
        return days

    def show_time(self) -> str:
        """Show current time in the game."""
        h = (self.current_time // 60) % 24
        m = self.current_time % 60
        return f'{h:02}:{m:02}'

    class CornFarm:
        """Represents corn farm and its state."""

        def __init__(self) -> None:
            """Initialize parameters of corn farm."""
            self.offer = 35
            self.price = 25

        def can_buy_corn(self, amount: int, hero, truck) -> bool:
            """Checks hero available to buy a given amount of corn."""
            if amount > self.offer:
                return False
            if hero.cash < amount * self.price:
                return False
            if truck.truck_space < amount:
                return False
            return True

        def buy(self, amount: int, hero, truck) -> None:
            """Make the purchase if it's possible."""
            if not self.can_buy_corn(amount, hero, truck):
                return
            self.offer -= amount
            hero.cash -= amount * self.price
            truck.truck_space -= amount
            truck.cargo['corn'] += amount

    class GruberGasStation:
        """Represents Gruber's gas station."""

        def __init__(self) -> None:
            """
            Initialize Gruber's gas station with fuel's price.
            Price is for 5 liters of fuel.
            """
            self.price = 7

        def can_fill_up(self, amount: int, hero, truck) -> bool:
            """Checks if hero can fill up the truck."""
            if hero.cash < (amount / 5) * self.price or truck.fuel + amount > 100:
                return False
            return True

        def fill_up(self, amount: int, hero, truck) -> None:
            """Fill ip the truck if it's possible."""
            if not self.can_fill_up(amount, hero, truck):
                return
            hero.cash -= int((amount / 5) * self.price)
            truck.fuel += amount


class Hero:
    """Represents the hero and his personal state."""

    def __init__(self):
        """Initialize the hero with default health, hanger, fatigue, cash."""
        self.health = 100
        self.fatigue = 100
        self.hanger = 100
        self.cash = 200
        self.ammo = 0
        self.stingrays_member = False

    def is_ammo(self) -> str:
        """Checks if the character has ammo for shotgun."""
        if self.ammo != 0:
            return f'Shotgun: {self.ammo} shells\n'
        return ''

    def is_stingrays_member(self) -> str:
        """
        Checks if the character is Stingrays gang member.

        :return: str for hero part in the state panel.
        """
        if self.stingrays_member == True:
            return f'Stingray tattoo\n'
        return ''


class Truck:
    """Represents the truck and its state."""

    def __init__(self) -> None:
        """Initialize the truck with default truck condition, fuel, space available."""
        self.truck_condition = 100
        self.fuel = 100
        self.truck_space = 10
        self.cargo = {'coal': 0, 'corn': 0}
        self.avg_speed = 70  # Assume the average truck speed is 70 km/h
        self.avg_fuel_consumption = 10  # Assume the average truck fuel consumption is 12 l/100km
        self.passenger = {}


class GameState:
    """Main container for the game state."""

    def __init__(self) -> None:
        """Initialize the full game state with default world, hero and truck."""
        self.world = World()
        self.hero = Hero()
        self.truck = Truck()
        self.locations = {}
        self.invisible_options = {
            'biker_defeated',
            'go_to_rockers_is_stingray',
            'treat_everyone_is_stingray',
            'treat_everyone_is_coward',
        }
