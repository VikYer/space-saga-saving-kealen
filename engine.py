import random

from game_state import GameState


class Engine:
    """
    Core gameplay logic for Space Saga.

    This class is responsible for processing player actions and
    applying their effects to the current game state. It acts as
    the "game engine", keeping all rules, calculations, and
    random events separated from the user interface.
    """

    def __init__(self, state: GameState):
        """Initialize game engine with game state values."""
        self.state = state

        # Allowed function list to call from location_actions.json
        self.allowed_functions = {
            'repair_lorry': self.get_new_truck,
            'buy_corn_1': self.buy_corn,
            'buy_corn_2': self.buy_corn,
            'buy_corn_3': self.buy_corn,
            'buy_corn_5': self.buy_corn,
            'buy_corn_10': self.buy_corn,
            'take_drox': self.take_drox,
            'treat_everyone': self.treat_everyone,
            'hit_stomach': self.hit_stomach,
            'sleep_in_bar': self.sleep_in_bar,
            'treat_everyone_is_stingray': self.treat_everyone_is_stingray,
        }

    def run_action(self, action_name: str, args: dict | None) -> None:
        """Move the action with the name from the allow list."""
        if not action_name:
            return
        fn = self.allowed_functions.get(action_name)
        if not fn:
            return
        fn(args or {})

    def apply_effect(self, effects: dict | None) -> None:
        """Handle support base game state changes."""
        if not effects:
            self.state.world.current_time += 1
            return

        if 'distance' in effects:
            distance = effects['distance']
            self.drive(distance)

        if 'time' in effects:
            self.state.world.current_time += effects['time']

        if 'cash' in effects:
            self.state.hero.cash += effects['cash']

        # Hero health, fatigue and hanger max level is 100
        if 'health' in effects:
            self.state.hero.health = min(self.state.hero.health + effects['health'], 100)
        if 'fatigue' in effects:
            self.state.hero.fatigue = min(self.state.hero.fatigue + effects['fatigue'], 100)
        if 'hanger' in effects:
            self.state.hero.hanger = min(self.state.hero.hanger + effects['hanger'], 100)

    def drive(self, distance: int) -> None:
        """
        Simulate driving the truck for a given distance.

        Truck speed and fuel consumption depend on cargo value.
        """
        load = 0
        for cargo in self.state.truck.cargo.values():
            load += cargo

        # Each ton of cargo increases truck fuel consumption by 0.2 l
        fuel_consumption = self.state.truck.avg_fuel_consumption + load * 0.2
        used_fuel = round((distance / 100) * fuel_consumption)
        self.state.truck.fuel -= used_fuel

        # Each ton of cargo reduce truck speed by 2 km/h
        speed = self.state.truck.avg_speed - load * 2
        time = round((distance / speed) * 60)
        self.state.world.current_time += time

    def get_new_truck(self, args: dict) -> None:
        """
        Hero get new truck (has other parameters) by repairing it with previous truck parts.
        Changing locations description.
        """
        self.state.truck.truck_space += args.get('load_change', 0)
        self.state.truck.avg_speed += args.get('speed_change', 0)
        self.state.truck.avg_fuel_consumption += args.get('fuel_consumption_change', 0)

        self.state.invisible_options.add('inspect_lorry')
        self.state.locations[self.state.world.current_location][
            'description'] = (
            f'You stop at a big T-shaped canyon. A small river shines at the bottom. '
            f'Two bridges — on the western and northern sides of the ravine — are destroyed. '
            f'At the bottom of the canyon, you notice a wrecked lorry. '
            f'It looks like it\'s yours...'
        )
        self.state.locations['Forsaken Iridium Mines - West'][
            'description'] = (
            'You stop at a big T-shaped canyon. A small river shines at the bottom and, '
            'it seems, a broken car, looking like your old truck. Two bridges – '
            'to the east and to the north – are broken. '
            'It looks like one of them went to the iridium mines.'
        )

    def buy_corn(self, args: dict) -> None:
        """Corn purchase on the farm."""
        amount = args.get('corn')
        self.state.world.corn_farm.buy(amount, self.state.hero, self.state.truck)

    def play_slot_machine(self) -> str:
        """
        Simulates playing slot machine.

        Machine reels has numbers from 1 to 7.
        Double match - win 2 cr.
        Triple match - win 25 cr.
        """
        first_reels = random.randint(1, 7)
        second_reels = random.randint(1, 7)
        third_reels = random.randint(1, 7)

        result = f'{first_reels} <---> {second_reels} <---> {third_reels}\n\n'

        if first_reels == second_reels == third_reels:
            self.state.hero.cash += 25
            return (
                f'{result}'
                f'A triple match! 25 credits dropped into the tray.'
            )
        elif first_reels == second_reels or second_reels == third_reels or first_reels == third_reels:
            self.state.hero.cash += 2
            return (
                f'{result}'
                f'A double match! 2 credits dropped into the tray.'
            )
        else:
            return (
                f'{result}'
                f'You have lost.'
            )

    def take_drox(self, args) -> None:
        """
        Start of the quest with the delivery of drox to the city.
        Add drox to the passenger dictionary (passenger: destination).
        The quest is one-time only.
        """
        self.state.truck.passenger['drox'] = 'Brackenbridge'
        self.state.invisible_options.add('go_to_drox')

    def drox_delivered(self) -> None:
        """The reward for delivering drox to the city is a shotgun with 6 shells."""
        self.state.hero.ammo += 6
        del self.state.truck.passenger['drox']

    def treat_everyone(self, args) -> None:
        """The party at the bar tires the hero."""
        self.state.hero.fatigue = 19
        self.state.world.biker_mood = 0

    def _biker_attacks(self) -> str:
        """
        Simulate the single bikers hit after party in the Stingray bar.

        - hit on the head reduces hero's health by 20;
        - hit in the stomach reduces hero's health by 7.

        :return: kind of attack for dynamic description.
        """
        hit = random.randint(0, 1)
        if hit == 0:
            self.state.hero.health -= 20
            return ('The biker landed a heavy blow on your head. '
                    'Sparks danced before your eyes. '
                    'The crowd cheered and whistled with joy.')
        else:
            self.state.hero.health -= 7
            return ('The biker hit you twice in the stomach. '
                    'For a moment you lost your breath. '
                    'A crooked smile crossed his face, but too early — '
                    'you quickly recovered.')

    def hit_stomach(self,args):
        """
        Hit on stomach causes the biker's mood to worsen.

        Biker looks determined -> Biker is careful -> Biker is afraid
        (is reflected in state_panel)
        """
        if self.state.world.biker_mood <= 3:
            self.state.world.biker_mood += 1

    def defeat_biker(self) -> None:
        """Hero becomes a member of the Stingrays gang."""
        self.state.world.biker_mood = None
        self.state.hero.stingrays_member = True
        self.state.world.current_time += 90

    def sleep_in_bar(self, args) -> None:
        """After joining the gang, the hero gets cheaper accommodation at the bar."""
        if self.state.hero.stingrays_member:
            self.state.hero.cash -= 5
        else:
            self.state.hero.cash -= 10

    def treat_everyone_is_stingray(self, args) -> None:
        """The party at the bar with new Stingrays friends tires the hero."""
        self.state.hero.fatigue = 19
