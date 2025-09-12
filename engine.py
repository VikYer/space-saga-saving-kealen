import random
from datetime import datetime

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
            'not_fighting_with_biker': self.not_fighting_with_biker,
            'gruber_fill_up_5': self.gruber_fill_up,
            'gruber_fill_up_15': self.gruber_fill_up,
            'repair_truck': self.repair_truck,
            'extend_trunk': self.extend_trunk,
            'upgrade_truck': self.upgrade_truck,
            'sell_all_coal': self.sell_all_coal,
            'sell_all_scrap': self.sell_all_scrap,
            'back_nothing_interesting': self.back_nothing_interesting,
            'back_meet_beggar': self.meet_beggar,
            'back_conflict_with_hooligans': self.back_conflict_with_hooligans,
            'back_stolen_money': self.back_stolen_money,
            'wait_restaurant_opening': self.wait_restaurant_opening,
            'back_to_square': self.back_to_square,
            'buy_scrap_1': self.buy_scrap,
            'buy_scrap_2': self.buy_scrap,
            'buy_scrap_3': self.buy_scrap,
            'buy_scrap_5': self.buy_scrap,
            'dosage_1_5': self.dosage_1_5,
            'leave_marshal': self.leave_marshal,
            'swim': self.swim,
            'swim_more': self.swim,
            'leave_lake': self.leave_lake,
            'three_swims': self.three_swims,
            'buy_coal_1': self.buy_coal,
            'buy_coal_2': self.buy_coal,
            'buy_coal_3': self.buy_coal,
            'buy_coal_5': self.buy_coal,
            'sell_all_corn': self.sell_all_corn,
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
        self.state.truck.upgrade_load_capacity = False
        self.state.truck.blades_on_wheels = False
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
        self.state.invisible_options.add('ask_barman_about_drox')

    def drox_delivered(self) -> None:
        """The reward for delivering drox to the city is a shotgun with 6 shells."""
        self.state.hero.has_shotgun = True
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
            self.state.hero.health -= 25
            return ('The biker landed a heavy blow on your head. '
                    'Sparks danced before your eyes. '
                    'The crowd cheered and whistled with joy.')
        else:
            self.state.hero.health -= 10
            return ('The biker hit you twice in the stomach. '
                    'For a moment you lost your breath. '
                    'A crooked smile crossed his face, but too early — '
                    'you quickly recovered.')

    def hit_stomach(self, args):
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
        self.state.invisible_options.discard('biker_defeated')
        self.state.invisible_options.add('go_to_rockers')
        self.state.invisible_options.discard('go_to_rockers_is_stingray')
        self.state.invisible_options.add('treat_everyone')
        self.state.invisible_options.discard('treat_everyone_is_stingray')

    def sleep_in_bar(self, args) -> None:
        """After joining the gang, the hero gets cheaper accommodation at the bar."""
        self.state.hero.fatigue = 89
        if self.state.hero.stingrays_member:
            self.state.hero.cash -= 5
        else:
            self.state.hero.cash -= 10

    def treat_everyone_is_stingray(self, args) -> None:
        """The party at the bar with new Stingrays friends tires the hero."""
        self.state.hero.fatigue = 19

    def not_fighting_with_biker(self, args) -> None:
        """
        After starting a fight with a biker, the hero gives up.
        Chance to join Stingrays gang is lost.
        """
        self.state.world.biker_mood = None
        self.state.invisible_options.add('treat_everyone')
        self.state.invisible_options.discard('treat_everyone_is_coward')

    def gruber_fill_up(self, args: dict) -> None:
        """Hero fills up the truck on the Gruber's gas station."""
        amount = args.get('fuel')
        self.state.world.gruber_gas_station.fill_up(amount, self.state.hero, self.state.truck)

    def bolt_repair_cost(self) -> int:
        """Bolt estimates the repairing cost of the truck."""
        cost = 100 - self.state.truck.truck_condition
        return cost

    def repair_truck(self, args) -> None:
        """Simulate truck repair."""
        self.state.hero.cash -= self.bolt_repair_cost()
        self.state.truck.truck_condition = 100

    def has_scrap_for_truck_upgrade(self) -> bool:
        """Checks if hero has enough scrap for truck upgrading."""
        if self.state.truck.cargo.get('scrap') < 5:
            return False
        return True

    def extend_trunk(self, args) -> None:
        """Mechanic increase truck load capacity."""
        self.state.truck.truck_space += 2
        self.state.truck.upgrade_load_capacity = True

    def upgrade_truck(self, args) -> None:
        """Mechanic welds sharp blades onto truck wheels."""
        self.state.truck.blades_on_wheels = True
        self.state.truck.cargo['scrap'] -= 5

    def sell_all_coal(self, args) -> None:
        """Hero sells all coal for factory in the city."""
        self.state.hero.cash += 12 * self.state.truck.cargo.get('coal')
        self.state.truck.cargo['coal'] = 0

    def sell_all_scrap(self, args) -> None:
        """Hero sells all scarp for factory in the city."""
        self.state.hero.cash += 23 * self.state.truck.cargo.get('scrap')
        self.state.truck.cargo['scrap'] = 0

    def randomize_city_exploration_event(self) -> None:
        """
        Randomizes events during the hero's walks around the city.
        During the day and at night, possible events and their probability of occurrence differ.
        """
        if self._is_time_in_range('23:00', '05:00'):
            self.state.discover_city_event = random.choices(
                ['back_nothing_interesting',
                 'meet_beggar',
                 'back_conflict_with_hooligans'],
                weights=[0.45, 0.45, 0.1],
                k=1
            )[0]
        else:
            self.state.discover_city_event = random.choices(
                ['back_stolen_money',
                 'back_nothing_interesting',
                 'meet_beggar'],
                weights=[0.2, 0.4, 0.4],
                k=1
            )[0]
        self.state.invisible_options.discard(self.state.discover_city_event)

    def _is_time_in_range(self, start: str, end: str) -> bool:
        """Checks if the current time is in the range [start, end]."""
        t = datetime.strptime(self.state.world.show_time(), '%H:%M').time()
        t_start = datetime.strptime(start, '%H:%M').time()
        t_end = datetime.strptime(end, '%H:%M').time()

        if t_start <= t_end:
            # Supports ranges that do not pass through midnight
            return t_start <= t and t <= t_end
        else:
            # Supports ranges that cross midnight
            return t >= t_start or t <= t_end

    def back_stolen_money(self, args) -> None:
        """Hides this dynamic method."""
        self.state.hero.cash = max(0, self.state.hero.cash - 7)
        self.state.invisible_options.add('back_stolen_money')
        self.state.discover_city_event = None

    def back_nothing_interesting(self, args) -> None:
        """Hides this dynamic method."""
        self.state.invisible_options.add('back_nothing_interesting')
        self.state.discover_city_event = None

    def meet_beggar(self, args) -> None:
        """Hides this dynamic method."""
        self.state.invisible_options.add('meet_beggar')
        self.state.discover_city_event = None

    def back_conflict_with_hooligans(self, args) -> None:
        """Hides this dynamic method."""
        self.state.invisible_options.add('back_conflict_with_hooligans')
        self.state.discover_city_event = None

    def wait_restaurant_opening(self, args) -> None:
        """Simulate the hero is waiting for the restaurant opening."""
        self.state.invisible_options.add('wait_restaurant_opening')

        self.state.invisible_options.discard('order_root')
        self.state.invisible_options.discard('order_wine')
        self.state.invisible_options.discard('order_tail')
        self.state.invisible_options.discard('order_beaver')
        self.state.invisible_options.discard('order_cactus')

        opening_time = datetime.strptime('09:01', '%H:%M')
        curr_time = datetime.strptime(self.state.world.show_time(), '%H:%M')
        self.state.world.current_time += int((opening_time - curr_time).total_seconds() / 60)

    def back_to_square(self, args) -> None:
        """
        The hero leaves the restaurant - all its options become invisible
        so its can be dynamically reformed during the next visit.
        """
        self.state.invisible_options.add('order_root')
        self.state.invisible_options.add('order_wine')
        self.state.invisible_options.add('order_tail')
        self.state.invisible_options.add('order_beaver')
        self.state.invisible_options.add('order_cactus')
        self.state.invisible_options.add('wait_restaurant_opening')

    def buy_scrap(self, args: dict) -> None:
        """Scrap purchase on the farm."""
        amount = args.get('scrap')
        self.state.world.wreckyard.buy(amount, self.state.hero, self.state.truck)

    def dosage_1_5(self, args) -> None:
        """Hero obtains ammunition by suggesting the correct dose of the substance to the marshal's chemist."""
        self.state.hero.ammo += 15

    def leave_marshal(self, args) -> None:
        """Hide dialogue options with the marshal leading to getting ammo for shotgun."""
        self.state.invisible_options.add('ask_marshal_about_weapon')

    def swim(self, args) -> None:
        """Count swims quantity in one cycle."""
        self.state.hero.swims_qty += 1

        if self.state.hero.swims_qty == 3 and self.state.hero.health < 40:
            self.state.hero.health = 40

        if self.state.hero.swims_qty == 3:
            self.state.invisible_options.add('swim_more')
            self.state.invisible_options.add('leave_lake')
            self.state.invisible_options.discard('three_swims')

    def leave_lake(self, args) -> None:
        """Resets the swimming counter after leaving the lake."""
        self.state.hero.swims_qty = 0

    def three_swims(self, args) -> None:
        """Restore the default options for the lake location after leaving it."""
        self.state.hero.swims_qty = 0

        self.state.invisible_options.discard('swim_more')
        self.state.invisible_options.discard('leave_lake')
        self.state.invisible_options.add('three_swims')

    def buy_coal(self, args: dict) -> None:
        """Coal purchase in the mine."""
        amount = args.get('coal')
        self.state.world.mine.buy(amount, self.state.hero, self.state.truck)

    def sell_all_corn(self, args) -> None:
        """Hero sells all corn in the mining settlement."""
        self.state.hero.cash += 45 * self.state.truck.cargo.get('corn')
        self.state.truck.cargo['corn'] = 0

    def work_in_mine(self) -> int:
        """"""
        earned_money = random.choice([2, 3])
        self.state.hero.cash += earned_money
        return earned_money
