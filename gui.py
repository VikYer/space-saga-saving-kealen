from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, ScrollableContainer
from textual.widgets import Static, Footer, OptionList
import json

from textual.widgets._option_list import Option

from engine import Engine
from map import MAP, MAP_LEGEND


class SpaceSaga(App):
    """Main application class for Space Saga: Saving Kealen, a terminal based text quest."""

    def __init__(self, state, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.engine = Engine(state)

    options_stack = []

    try:
        with open('location_actions.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
    except FileNotFoundError:
        print('File with locations was not found.')
        locations = {}
    except json.JSONDecodeError as e:
        print(f'Error in the file with locations: {e}')
        locations = {}

    CSS_PATH = 'style.tcss'

    def compose(self) -> ComposeResult:
        """
        Build the UI components that form main layout:
        Includes:
        - game info panel;
        - game state panel;
        - command panel;
        - footer.
        """
        self.map_widget = Static(MAP, id='map')
        self.legend_widget = Static(MAP_LEGEND, id='map-legend')
        self.quest_text = Static('', id='quest-text')
        self.quest_panel = ScrollableContainer(
            self.quest_text,
            id='quest-panel'
        )
        self.state_panel = Static('', id='state-panel')
        self.command_panel = OptionList(id='command-panel')
        yield Horizontal(
            Container(
                Horizontal(self.map_widget, self.legend_widget),
                self.quest_text,
                id='left-part'
            ),
            Container(
                self.state_panel,
                id='right-part'
            ),
        )
        yield Container(
            self.command_panel,
            id='bottom-part'
        )
        yield Footer()

    def on_mount(self) -> None:
        self.sp = StatePanel(self.state_panel, self.state)
        self.sp.update_state_panel()
        self.show_location('Spaceport')

    def show_location(self, location_name: str) -> None:
        """Display location description in quest-text and available commands in command-panel."""
        self.state.world.current_location = location_name
        self.options_stack = []

        location = self.locations.get(location_name)
        if not location:
            return

        self.quest_text.update(location.get('description'))

        options = location.get('options')
        self._show_options(options)

    def _show_options(self, options: dict) -> None:
        """Helper: display command options in command-panel."""
        self.command_panel.clear_options()
        for opt_id, opt in options.items():
            self.command_panel.add_option(Option(opt.get('text'), opt_id))
        self.set_focus(self.command_panel)
        self.command_panel.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection from command-panel."""
        location = self.locations.get(self.state.world.current_location)
        if not location:
            return

        options = location.get('options')

        for el in self.options_stack:
            parent = options.get(el)
            if not parent:
                return
            options = parent.get('options')

        option = options.get(event.option_id)
        if not option:
            return

        effects = option.get('effects')
        self.engine.apply_effect(effects)

        if 'goto' in option:
            self.show_location(option['goto'])

        if 'description' in option:
            self.quest_text.update(option['description'])

        if 'options' in option:
            self.options_stack.append(event.option_id)
            self._show_options(option['options'])
            return

        if event.option_id == 'back':
            if self.options_stack:
                self.options_stack.pop()

                options = location.get('options')
                parent_option = None

                for el in self.options_stack:
                    parent_option = options.get(el)
                    options = parent_option.get('options')

                if parent_option and 'description' in parent_option:
                    self.quest_text.update(parent_option['description'])
                else:
                    self.quest_text.update(location.get('description'))

                self._show_options(options)

            else:
                self.quest_text.update(location.get("description"))
                self._show_options(location.get('options'))
            return

        self.sp.update_state_panel()


class StatePanel:
    """Handles rendering of game state into state panel."""

    def __init__(self, state_panel_widget: Static, game_state):
        """Initialize state panel with game state values."""
        self.state_panel_widget = state_panel_widget
        self.game_state = game_state

    @staticmethod
    def _grade(param: str, value: int) -> str:
        """Helper: return a textual level for health, fatigue and hunger."""
        if param == 'health':
            levels = ['[red]critical[/red]', '[yellow]weak[/yellow]', '[yellow]wounded[/yellow]', 'healthy',
                      'full strength']
        elif param == 'fatigue':
            levels = ['[red]exhausted[/red]', '[yellow]very tired[/yellow]', '[yellow]weary[/yellow]', 'rested',
                      'energetic']
        elif param == 'hanger':
            levels = ['[red]starving[/red]', '[yellow]hungry[/yellow]', '[yellow]peckish[/yellow]', 'satisfied',
                      'well fed']
        else:
            levels =['unknown']

        index = min(value // 20, 4)
        return levels[index]

    def update_state_panel(self) -> None:
        """Update game state panel with current game state."""
        world = self.game_state.world
        hero = self.game_state.hero
        truck = self.game_state.truck

        if truck.fuel <= 20:
            fuel_color = 'red'

        text = (
            f'Days passed: {world.days}\n'
            f'Time: {world.show_time()}\n'
            f'Current location: {world.current_location}\n\n'
            f'HERO:\n'
            f'Health: {self._grade('health', hero.health)}\n'
            f'Fatigue: {self._grade('fatigue', hero.fatigue)}\n'
            f'Hanger: {self._grade('hanger', hero.hanger)}\n'
            f'Cash: {hero.cash}cr\n\n'
            f'TRUCK:\n'
            f'Truck condition: {truck.truck_condition}%\n'
            f'Fuel: [{fuel_color}]{truck.fuel}[/{fuel_color}] l\n'
            f'Space available: {truck.truck_space}\n'
        )

        self.state_panel_widget.update(text)
