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

    def apply_effect(self, effects: dict) -> None:
        """Handle support base game state changes."""
        if not effects:
            return

        if 'distance' in effects:
            distance = effects.get('distance')
            self._drive(distance)

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
