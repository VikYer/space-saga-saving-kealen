from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Static, Footer


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
                Static('Game info panel', id='info-panel'),
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
