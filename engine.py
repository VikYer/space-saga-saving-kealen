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
            "repair_lorry": self._repair_lorry,
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
            self._drive(distance)

        if 'time' in effects:
            self.state.world.current_time += effects['time']

    def _drive(self, distance: int) -> None:
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

    def _repair_lorry(self, args: dict)  -> None:
        """
        Hero get new truck (has other parameters) by repairing it with previous truck parts.
        Changing locations description.
        """
        self.state.truck.truck_space += args.get('load_change', 0)
        self.state.truck.avg_speed += args.get('speed_change', 0)
        self.state.truck.avg_fuel_consumption += args.get('fuel_consumption_change', 0)

        self.state.invisible_options.add('inspect_lorry')
        self.state.locations[self.state.world.current_location]['description'] = 'You stop at a big T-shaped canyon. A small river shines at the bottom. Two bridges — on the western and northern sides of the ravine — are destroyed. At the bottom of the canyon, you notice a wrecked lorry. It looks like it\'s yours...'
        self.state.locations['Forsaken Iridium Mines - West']['description'] = 'You stop at a big T-shaped canyon. A small river shines at the bottom and, it seems, a broken car, looking like your old truck. Two bridges – to the east and to the north – are broken. It looks like one of them went to the iridium mines.'
