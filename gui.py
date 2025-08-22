from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, ScrollableContainer
from textual.widgets import Static, Footer, OptionList
import json

from map import MAP, MAP_LEGEND


class SpaceSaga(App):
    """Main application class for Space Saga: Saving Kealen, a terminal based text quest."""

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

    def on_mount(self):
        self.show_location('Corn Farm')

    def show_location(self, location_name: str) -> None:
        """Display location description in quest-text and available commands in command-panel"""
        location = self.locations[location_name]
        self.quest_text.update(location['description'])

        options = location.get('options')
        self.command_panel.clear_options()
        for val in options.values():
            self.command_panel.add_option(val['text'])
        self.set_focus(self.command_panel)
        self.command_panel.highlighted = 0
