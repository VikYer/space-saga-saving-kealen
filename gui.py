from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, ScrollableContainer
from textual.widgets import Static, Footer, OptionList
import json

from textual.widgets._option_list import Option

from map import MAP, MAP_LEGEND


class SpaceSaga(App):
    """Main application class for Space Saga: Saving Kealen, a terminal based text quest."""

    current_location = ''
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
        self.state_panel = Static('Game State Panel', id='state-panel')
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
        self.show_location('Spaceport')

    def show_location(self, location_name: str) -> None:
        """Display location description in quest-text and available commands in command-panel"""
        self.current_location = location_name
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
        location = self.locations.get(self.current_location)
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
