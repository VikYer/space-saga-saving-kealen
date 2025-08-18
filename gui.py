from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Static, Footer

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
        yield Horizontal(
            Container(
                Horizontal(
                    Static(MAP, id='map'),
                    Static(MAP_LEGEND, id='map-legend'),
                ),

                Static('Quest Text', id='quest-text'),
                id='left-part'
            ),
            Container(
                Static('Game state panel', id='state-panel'),
                id='right-part'
            ),
        )
        yield Container(
            Static('Command panel', id='command-panel'),
            id='bottom-part'
        )
        yield Footer()
