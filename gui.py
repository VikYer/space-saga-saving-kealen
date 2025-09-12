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
                    if not self.state.world.corn_farm.can_buy_corn(amount,
                                                                   self.state.hero,
                                                                   self.state.truck):
                        disabled = True

            # Show options for the Stingray bar location
            if self.state.world.current_location == 'The Stingray Bar':
                if opt_id == 'drink_port_wine' and self.state.hero.cash < 3:
                    disabled = True
                if opt_id == 'drink_cocktail' and self.state.hero.cash < 4:
                    disabled = True
                if opt_id == 'treat_everyone' and self.state.hero.cash < 50:
                    disabled = True
                if opt_id == 'eat_mushrooms_with_meat' and self.state.hero.cash < 6:
                    disabled = True
                if opt_id == 'sleep_in_bar':
                    if (not self.state.hero.stingrays_member and self.state.hero.cash < 10 or
                            (self.state.hero.stingrays_member and self.state.hero.cash < 5)):
                        disabled = True

            # Show options for Gruber's gas station
            if self.state.world.current_location == 'Gruber\'s Fuel Station':
                if opt_id.startswith('gruber_fill_up'):
                    amount = int(opt_id.split('_')[-1])
                    if not self.state.world.gruber_gas_station.can_fill_up(amount,
                                                                           self.state.hero,
                                                                           self.state.truck):
                        disabled = True

            # Show options for Bolt's garage
            if self.state.world.current_location == 'Bolt\'s Garage':
                if opt_id == 'fix_truck' and self.state.truck.truck_condition == 100:
                    disabled = True
                if opt_id == 'extend_trunk' and self.state.hero.cash < 50:
                    disabled = True
                if opt_id == 'extend_trunk' and self.state.truck.upgrade_load_capacity:
                    disabled = True
                if opt_id == 'upgrade_truck' and not self.engine.has_scrap_for_truck_upgrade():
                    disabled = True
                if opt_id == 'upgrade_truck' and self.state.truck.blades_on_wheels:
                    disabled = True

            # Show options for town
            if self.state.world.current_location == 'Brackenbridge':
                if opt_id == 'sell_all_coal' and self.state.truck.cargo.get('coal') == 0:
                    disabled = True
                if opt_id == 'sell_all_scrap' and self.state.truck.cargo.get('scrap') == 0:
                    disabled = True
                if opt_id == 'energy_treatment' and self.state.hero.cash < 50:
                    disabled = True
                if opt_id == 'energy_treatment' and self.state.hero.health == 100:
                    disabled = True
                if opt_id == 'rest' and self.state.hero.fatigue == 100:
                    disabled = True
                if opt_id == 'take_girl':
                    if self.state.hero.health == 100 and self.state.hero.fatigue == 100:
                        disabled = True
                if opt_id == 'coins_for_beggar' and self.state.hero.cash < 4:
                    disabled = True
                if opt_id == 'order_root' and self.state.hero.cash < 7:
                    disabled = True
                if opt_id == 'order_wine' and self.state.hero.cash < 9:
                    disabled = True
                if opt_id == 'order_tail' and self.state.hero.cash < 10:
                    disabled = True
                if opt_id == 'order_beaver' and self.state.hero.cash < 20:
                    disabled = True
                if opt_id == 'order_cactus' and self.state.hero.cash < 23:
                    disabled = True

            # Show option for wreckyard
            if self.state.world.current_location == 'Wreckyard':
                if opt_id.startswith('buy_scrap'):
                    amount = int(opt_id.split('_')[-1])
                    if not self.state.world.wreckyard.can_buy_scrap(amount,
                                                                    self.state.hero,
                                                                    self.state.truck):
                        disabled = True

            self.command_panel.add_option(Option(opt.get('text'), opt_id, disabled=disabled))

        if options:
            self.set_focus(self.command_panel)
            self.command_panel.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection from command-panel."""

        # Finish the quest to deliver drox to the city
        if event.option_id == 'drox_delivered':
            self.show_location('Brackenbridge')
            return

        # City exploration has a few options
        if event.option_id == 'discover_city':
            self.engine.randomize_city_exploration_event()

        # Restaurant is open from 9:00 until the last visitor after 23:59
        if event.option_id == 'go_to_restaurant':
            if self.engine._is_time_in_range('09:00', '23:59'):
                self.state.invisible_options.discard('order_root')
                self.state.invisible_options.discard('order_wine')
                self.state.invisible_options.discard('order_tail')
                self.state.invisible_options.discard('order_beaver')
                self.state.invisible_options.discard('order_cactus')
            else:
                self.state.invisible_options.discard('wait_restaurant_opening')

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

        # Drox delivery quest completion
        if self.state.world.current_location == 'Brackenbridge':
            if 'drox' in self.state.truck.passenger:
                self.quest_text.update(
                    f'You stopped in the city square and tried to wake up the drox. '
                    f'He didn’t wake at first, so you shook him for five minutes until he opened his eyes.\n'
                    f'– What? What is it? – he asked sleepily.\n'
                    f'– We\'re here!'
                    f'– Really? Thanks, brother. I came to work at the factory now, '
                    f'no more wild life for me. So take my trophy shotgun and six shells — it may help you.\n'
                    f'He handed you a small shotgun with ammo, said goodbye, '
                    f'and walked toward the factory until he disappeared.'
                )
                self.engine.drox_delivered()
                self.command_panel.clear_options()
                self.command_panel.add_option(Option('Next', 'drox_delivered'))
                self.set_focus(self.command_panel)
                self.command_panel.highlighted = 0
                return

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

        if event.option_id.startswith('back'):
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

        # Dynamic quest text depending on the quantity and price of corn.
        if option_name == 'approach_farm':
            return (
                'Your car was parked right in front of the gate of the farmhouse. '
                'A young man in a hat with a cane in his teeth was looking at you from the window:\n\n'
                f'– We currently have {self.state.world.corn_farm.offer} tonnes '
                'of corn, packed in barrels, one tonne each. '
                f'We sell them for {self.state.world.corn_farm.price} credits per barrel. '
                'And if you want to sell something yourself, sorry, '
                'we\'re not buying anything. We have everything we need.'
            )

        if option_name.startswith('buy_corn'):
            return (
                f'– We currently have {self.state.world.corn_farm.offer} tonnes '
                'of corn, packed in barrels, one tonne each. '
                f'We sell them for {self.state.world.corn_farm.price} credits per barrel. '
                'And if you want to sell something yourself, sorry, '
                'we\'re not buying anything. We have everything we need.'
            )

        # The bartender's greeting depends on whether the hero is a member of the gang.
        if option_name == 'go_to_barman':
            if self.state.hero.stingrays_member:
                text = 'What do you want, our little stingray? – asked the barman, smiling from ear to ear.'
            else:
                text = '– Did you want something? – the bartender asked.'
            return (
                f'{text}\n\n'
                'Behind him you notice a sign:\n'
                '\"Fried meat with mushrooms – 6 credits. '
                'A bed for 6 hours – 10 credits (for Stingrays: 5 credits)\"'
            )

        # Hero play slot machine in the bar
        if option_name == 'play_slot_machine':
            result = self.engine.play_slot_machine()
            self.sp.update_state_panel()
            return (
                'The reels spun wildly and stopped at the combination:\n\n'
                f'{result}'
            )

        # Fight with biker. Hero does not take any action against the opponent.
        # If the biker is afraid of the hero, he waits; otherwise, he attacks.
        if option_name == 'do_nothing_against_biker':
            if self.state.world.biker_mood < 3:
                biker_attack_result = self.engine._biker_attacks()
                self.sp.update_state_panel()
                return (
                    f'{biker_attack_result}\n\n'
                    'You stand in front of a drunk biker. He looks unfriendly. '
                    'If you have the strength, maybe it’s time to punch that arrogant face.'
                )
            else:
                return 'The biker did nothing. It looked like he was waiting for your move.'

        # Fight with biker. Hero  hits the biker on the head, but to no avail.
        # Hero receives a blow in return.
        # If biker is afraid, he waits for hero's reaction.
        if option_name == 'hit_head':
            biker_attack_result = self.engine._biker_attacks()
            self.sp.update_state_panel()
            if self.state.world.biker_mood < 3:
                return (
                    'You tried to hit your opponent, but your poor condition betrayed you. '
                    'Your hand missed his ear, and you stumbled onto him instead. '
                    'The biker quickly used this chance and threw you to the ground, '
                    'while everyone laughed. Not wanting things to '
                    'get worse, you stood back up.\n\n'
                    f'{biker_attack_result}'
                )
            else:
                return (
                    'You tried to hit your opponent, but your poor condition betrayed you. '
                    'Your hand missed his ear, and you stumbled onto him instead. '
                    'The biker quickly used this chance and threw you to the ground, '
                    'while everyone laughed. Not wanting things to '
                    'get worse, you stood back up.\n\n'
                    'The biker did nothing. It looked like he was waiting for your move.'
                )

        # Fight with biker. Hero  hits the biker on the stomach -
        # biker's fighting spirit is waning.
        # Hero receives a blow in return.
        # If biker is afraid, he waits for hero's reaction.
        if option_name == 'hit_stomach':
            if self.state.world.biker_mood < 3:
                biker_attack_result = self.engine._biker_attacks()
                self.sp.update_state_panel()
                return (
                    'You hit the biker in the stomach. Not as strong as a punch to the head, '
                    'but at least hard to miss.\n\n'
                    f'{biker_attack_result}'
                )
            elif self.state.world.biker_mood == 3:
                return (
                    'You hit the biker in the stomach. Not as strong as a punch to the head, '
                    'but at least hard to miss.\n\n'
                    'The biker did nothing. It looked like he was waiting for your move.'
                )
            else:
                self.engine.defeat_biker()
                self.state.invisible_options.add('back_to_fight')
                return ('– Alright, alright. Good job, – said the biker, raising his hands. '
                        'The crowd rushed to you and started tossing you up in the air. '
                        'Suddenly, you blacked out again… '
                        'You woke up at the entrance of the bar. '
                        'Your right shoulder hurt badly. Looking at it, you saw '
                        'a fresh tattoo of a scorpion. Looks like you’re in the gang now!'
                        )

        # Dynamic car repair pricing
        if option_name == 'fix_truck' and self.state.world.current_location == 'Bolt\'s Garage':
            return ('Bolt quickly looked over the car and said: '
                    f'– So, here the repair will cost {self.engine.bolt_repair_cost()} credits. '
                    'You understand, I don’t use cheap parts like Dex, '
                    'so my prices are real. But your car will be like new! Well, do we fix it?'
                    )

        # Hero's exploration of the city
        if self.state.world.current_location == 'Brackenbridge' and option_name == 'discover_city':
            if self.state.discover_city_event == 'back_stolen_money':
                return (
                    'You walked around for a long time but found nothing except old houses. '
                    'It seemed that all the interesting places were near the main square. '
                    'With that thought, you went back. When you put your hand in your pocket, '
                    'you saw that someone had stolen a few credits '
                    'This did not make your mood any better.'
                )
            if self.state.discover_city_event == 'back_nothing_interesting':
                return (
                    'You wandered for a long time but found only old houses. '
                    'It seemed all the interesting places were near the main square. '
                    'With that thought, you went back to where your trip began.'
                )
            if self.state.discover_city_event == 'meet_beggar':
                return (
                    'You wandered for a long time but found only old shabby houses. '
                    'It seemed all the real life was near the main square. '
                    'Just as you were about to head back, you noticed a beggar '
                    'sitting on the sidewalk, asking for coins.'
                )
            if self.state.discover_city_event == 'back_conflict_with_hooligans':
                return (
                    'You walked around but found only old houses. '
                    'On the way back, someone hit you from behind and you fell.\n'
                    'Three teenage punks stood over you. They looked tough together.\n'
                    'You got up, kicked one in the legs, broke another’s nose, '
                    'and the gang ran off. You were hurt too. Better not to walk here '
                    'at twilight – it’s their time.'
                )

        # Restaurant is open from 9:00 until the last visitor after 23:59
        if self.state.world.current_location == 'Brackenbridge' and option_name == 'go_to_restaurant':
            if self.engine._is_time_in_range('09:00', '23:59'):
                return (
                    'Grabbing the restaurant door handle, you noticed a sign on the glass:\n'
                    '\"Open. The restaurant operates daily: '
                    'from 9:00 until the last visitor after 23:59.\"\n\n'
                    'Noting this, you went inside.There weren’t many people, so you easily '
                    'found a table.\n'
                    '– Shall we order something? – asked the waiter, dressed in a neat suit, '
                    'handing you the menu. \nYou quickly looked through the options, '
                    'noting what you could afford and what was too expensive.'
                )
            else:
                return (
                    'A sign hangs on the door:\n'
                    '\"Closed.\n'
                    'The restaurant is open daily:\n'
                    'from 9:00 until the last guest after 23:59.\"'
                )

        # Dynamic quest text depending on the quantity and price of scrap
        if option_name == 'go_wreckyard':
            return (
                'The vehicle skillfully entered the scrapyard. You were about to '
                'delve deeper into the trash maze, but a three-meter-tall robot blocked '
                'your way. Rusty as it was, it looked impressive…\n\n'
                '– You’re in the Varnock brothers’ territory, gringo! – said the man '
                'inside the robot. – If you’re here on business, know this: we '
                f'currently have {self.state.world.wreckyard.offer} tons of scrap metal. '
                f'{self.state.world.wreckyard.price} credits per ton. '
                'The scrap is pressed and neatly packed—top quality stuff.'
            )

        if option_name.startswith('buy_scrap'):
            return (
                '– If you’re here on business, know this: we '
                f'currently have {self.state.world.wreckyard.offer} tons of scrap metal. '
                f'{self.state.world.wreckyard.price} credits per ton. '
                'The scrap is pressed and neatly packed—top quality stuff.'
            )

        # Hero swims in forrest lake
        if option_name == 'swim_more':
            if self.state.hero.swims_qty == 3 and self.state.hero.health <= 40:
                return (
                    'You kept swimming in the lake when suddenly you felt energy '
                    'filling your body and your wounds healing. Looks like '
                    'this pond has healing powers!\n'
                    'After a few minutes, the effect faded. In your current state, '
                    'the pond couldn’t help you any further. Realizing this, '
                    'you climbed out, dried off, got into your truck, and headed '
                    'back to the road.'
                )
            elif self.state.hero.swims_qty == 3 and self.state.hero.health > 40:
                return (
                    'You went swimming again. Mosquitoes buzzed over your head, '
                    'weeds got into your mouth — enough was enough! Tired of it all, '
                    'you climbed out, dried off, got into your truck, and drove '
                    'back to the road.'
                )
            else:
                return (
                    'You swam in the water for five minutes. In such water, '
                    'it didn’t give you much pleasure. Only made you feel more tired.'
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
                      '[yellow]very weak[/yellow]', '[yellow]badly wounded[/yellow]',
                      'bleeding', 'injured', 'hurt',
                      'scratched', 'bruised', 'unharmed']
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

        world_state = (
            f'Days passed: {world.show_days()}\n'
            f'Time: {world.show_time()}\n'
            f'Current location: {world.current_location}\n\n'
        )
        hero_state = (
            f'HERO:\n'
            f'Health: {self._grade('health', hero.health)}\n'
            f'Fatigue: {self._grade('fatigue', hero.fatigue)}\n'
            f'Hanger: {self._grade('hanger', hero.hanger)}\n'
            f'Cash: {hero.cash} cr\n'
        )
        if hero.is_stingrays_member():
            hero_state += f'{hero.is_stingrays_member()}'
        if hero.is_ammo():
            hero_state += f'{hero.is_ammo()}\n'

        truck_state = (
            f'\nTRUCK:\n'
            f'Truck condition: {truck.truck_condition}%\n'
            f'Fuel: [{fuel_color}]{truck.fuel}[/{fuel_color}] l\n'
            f'Available space: {truck.truck_space}\n'
        )
        if truck.upgrade_load_capacity:
            truck_state += 'Load capacity increased\n'

        if truck.blades_on_wheels:
            truck_state += 'Blades on the wheels\n'

        for goods, amount in truck.cargo.items():
            if amount > 0:
                truck_state += f'{goods.capitalize()}: {amount} t\n'

        if truck.passenger:
            for passang, destination in truck.passenger.items():
                truck_state += f'{passang} to {destination}'

        if world.biker_mood != None and world.biker_mood <= 4:
            biker_mood = world.biker_mood
            truck_state += f'\n{
            ('Biker looks determined', 'Biker is confident', 'Biker is careful',
             'Biker is afraid', 'Biker is afraid')[biker_mood]}'

        self.state_panel_widget.update(world_state + hero_state + truck_state)
