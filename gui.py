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

        try:
            with open('location_actions.json', 'r', encoding='utf-8') as f:
                self.state.locations = json.load(f)
        except FileNotFoundError:
            print('File with locations was not found.')
            self.state.locations = {}
        except json.JSONDecodeError as e:
            print(f'Error in the file with locations: {e}')
            self.state.locations = {}

    options_stack = []

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
        self.sp.update_state_panel()

        location = self.state.locations.get(location_name)
        if not location:
            return

        self.quest_text.update(location.get('description'))

        options = location.get('options')
        self._show_options(options)

    def _show_options(self, options: dict) -> None:
        """Helper: display command options in command-panel."""
        self.command_panel.clear_options()
        for opt_id, opt in options.items():

            disabled = False

            if hasattr(self.state, 'invisible_options') and opt_id in self.state.invisible_options:
                continue

            # Show options for corn farm location
            if self.state.world.current_location == "Corn Farm":
                if opt_id.startswith('buy_corn'):
                    amount = int(opt_id.split('_')[-1])
                    if not self.state.world.corn_farm.can_buy(amount,
                                                              self.state.hero,
                                                              self.state.truck):
                        disabled = True

            # Show option for the Stingray bar location
            if self.state.world.current_location == 'The Stingray Bar':
                if opt_id == 'drink_port_wine' and self.state.hero.cash < 3:
                    disabled = True
                if opt_id == 'drink_cocktail' and self.state.hero.cash < 4:
                    disabled = True
                if opt_id == 'treat_everyone' and self.state.hero.cash < 50:
                    disabled = True
                if opt_id == 'eat_mushrooms_with_meat' and self.state.hero.cash < 6:
                    disabled = True
                if opt_id == 'sleep' and self.state.hero.cash < 10:
                    disabled = True

            self.command_panel.add_option(Option(opt.get('text'), opt_id, disabled=disabled))

        if options:
            self.set_focus(self.command_panel)
            self.command_panel.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection from command-panel."""
        location = self.state.locations.get(self.state.world.current_location)
        if not location:
            return

        options = location.get('options')

        for el in self.options_stack:
            parent = options.get(el)
            self.sp.update_state_panel()
            if not parent:
                return
            options = parent.get('options')

        option = options.get(event.option_id)
        if not option:
            return

        # Handle support base game state changes
        effects = option.get('effects')
        self.engine.apply_effect(effects)

        # Handle specific game action
        action_name = event.option_id
        self.engine.run_action(action_name, effects)

        self.sp.update_state_panel()
        self._show_options(options)

        if 'goto' in option:
            self.show_location(option['goto'])

        # Check whether the description is generated dynamically
        if 'description' in option:
            if option['description'] == 'dynamic':
                self.quest_text.update(self._get_dynamic_description(event.option_id))
            else:
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
                    if parent_option['description'] == 'dynamic':
                        self.quest_text.update(self._get_dynamic_description(self.options_stack[-1]))
                    else:
                        self.quest_text.update(parent_option['description'])
                else:
                    self.quest_text.update(location.get('description'))

                self._show_options(options)

            else:
                self.quest_text.update(location.get("description"))
                self._show_options(location.get('options'))
            return

    def _get_dynamic_description(self, option_name: str) -> str:
        """Helper: generate a context-sensitive description text for the quest panel."""
        if option_name.startswith('buy_corn') or option_name == 'approach_farm':
            return (
                f'Your car was parked right in front of the gate of the farmhouse. '
                f'A young man in a hat with a cane in his teeth was looking at you from the window:\n\n'
                f'We currently have {self.state.world.corn_farm.offer} tonnes '
                f'of corn, packed in barrels, one tonne each. '
                f'We sell them for {self.state.world.corn_farm.price} credits per barrel. '
                f'And if you want to sell something yourself, sorry, '
                f'we\'re not buying anything. We have everything we need.'
            )
        return ''


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
            levels = ['[red]dying[/red]', '[red]critical[/red]',
                      '[yellow]weak[/yellow]', '[yellow]wounded[/yellow]',
                      'hurt', 'scratched', 'fine',
                      'healthy', 'strong', 'perfect']
        elif param == 'fatigue':
            levels = ['[red]unconscious[/red]', '[red]barely awake[/red]',
                      '[yellow]drained[/yellow]', '[yellow]exhausted[/yellow]',
                      'sleepy', 'tired', 'okay',
                      'active', 'rested', 'fresh']
        elif param == 'hanger':
            levels = ['[red]dying of hunger[/red]', '[red]faint[/red]',
                      '[yellow]weak from hanger[/yellow]', '[yellow]starving[/yellow]',
                      'very hangry', 'hungry', 'peckish',
                      'fed', 'satisfied', 'full']
        else:
            levels = ['unknown']

        index = min(value // 10, 9)
        return levels[index]

    def update_state_panel(self) -> None:
        """Update game state panel with current game state."""
        world = self.game_state.world
        hero = self.game_state.hero
        truck = self.game_state.truck

        fuel_color = 'red' if truck.fuel <= 25 else 'white'

        text = (
            f'Days passed: {world.days}\n'
            f'Time: {world.show_time()}\n'
            f'Current location: {world.current_location}\n\n'
            f'HERO:\n'
            f'Health: {self._grade('health', hero.health)}\n'
            f'Fatigue: {self._grade('fatigue', hero.fatigue)}\n'
            f'Hanger: {self._grade('hanger', hero.hanger)}\n'
            f'Cash: {hero.cash} cr\n\n'
            f'TRUCK:\n'
            f'Truck condition: {truck.truck_condition}%\n'
            f'Fuel: [{fuel_color}]{truck.fuel}[/{fuel_color}] l\n'
            f'Available space: {truck.truck_space}\n'
        )

        for goods, amount in truck.cargo.items():
            if amount > 0:
                text += f'{goods.capitalize()}: {amount} t\n'

        self.state_panel_widget.update(text)
