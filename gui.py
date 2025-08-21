from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Static, Footer, SelectionList

from map import MAP, MAP_LEGEND


class SpaceSaga(App):
    """Main application class for Space Saga: Saving Kealen, a terminal based text quest."""

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
        self.quest_text = Static('Quest Text')
        self.state_panel = Static('Game State Panel', id='state-panel')
        self.command_panel = Static('Command Panel', id='command-panel')
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
