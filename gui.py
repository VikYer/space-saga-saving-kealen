import random

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

            # Show option for trading house in the mining settlement
            if self.state.world.current_location == 'Mining Settlement':
                if opt_id.startswith('buy_coal'):
                    amount = int(opt_id.split('_')[-1])
                    if not self.state.world.mine.can_buy_coal(amount,
                                                              self.state.hero,
                                                              self.state.truck):
                        disabled = True
                if opt_id == 'sell_all_corn' and self.state.truck.cargo.get('corn') == 0:
                    disabled = True
                if opt_id == 'buy_porridge' and self.state.hero.cash == 0:
                    disabled = True
                if opt_id == 'sleep' and self.state.hero.fatigue == 100:
                    disabled = True

            # Show options for Dex's gas station
            if self.state.world.current_location == 'Dex\'s Fuel Station':
                if opt_id == 'about_fixing' and self.state.truck.truck_condition >= 75:
                    disabled = True
                if opt_id == 'back_dex_fix_truck':
                    if self.engine.dex_repair_cost() > self.state.hero.cash:
                        disabled = True
                if opt_id.startswith('dex_fill_up'):
                    amount = int(opt_id.split('_')[-1])
                    if not self.state.world.gruber_gas_station.can_fill_up(amount,
                                                                           self.state.hero,
                                                                           self.state.truck):
                        disabled = True

            # Show options for road healer
            if self.state.world.current_location == 'Road - healer':
                if opt_id == 'buy_legs' and self.state.hero.cash < 30:
                    disabled = True
                if opt_id == 'buy_eye' and self.state.hero.cash < 15:
                    disabled = True
                if opt_id == 'buy_broth' and self.state.hero.cash < 20:
                    disabled = True
                if opt_id == 'buy_fly' and self.state.hero.cash < 5:
                    disabled = True

            # Show options for fuel truck on the road
            if self.state.world.current_location == 'Road - fuel truck':
                if opt_id == 'buy_fuel' and self.state.hero.cash < 8:
                    disabled = True

            # Show options for damage truck on the road
            if self.state.world.current_location == 'Road - damage truck':
                if opt_id == 'back_after_buy_fuel' and self.state.hero.cash < 25:
                    disabled = True

            # Show options for mustang on the road
            if self.state.world.current_location == 'Road - mustang':
                if opt_id == 'back_after_buy_fuel' and self.state.hero.cash < 22:
                    disabled = True

            # Show options for pickup on the road
            if self.state.world.current_location == 'Road - pickup':
                if opt_id == 'back_after_sell_fuel' and self.state.truck.fuel < 21:
                    disabled = True

            # Show options for empty mustang on the road
            if self.state.world.current_location == 'Road - empty mustang':
                if opt_id == 'back_after_buy_fuel' and self.state.hero.cash < 18:
                    disabled = True
                if opt_id == 'back_after_buy_shell' and self.state.hero.cash < 1:
                    disabled = True

            self.command_panel.add_option(Option(opt.get('text'), opt_id, disabled=disabled))

        if options:
            self.set_focus(self.command_panel)
            self.command_panel.highlighted = 0

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection from command-panel."""

        # Finish the quest to deliver drox or policeman to the city
        if event.option_id == 'drox_delivered' or event.option_id == 'policeman_delivered':
            self.show_location('Brackenbridge')
            return

        # Finish the quest to deliver passenger from mine to the city
        if event.option_id == 'passenger_from_mine_to_city_delivered':
            self.show_location('Brackenbridge')
            return

        # Finish the quest to deliver passenger from city to mine
        if event.option_id == 'passenger_from_city_to_mine_delivered':
            self.show_location('Mining Settlement')
            return

        # Finish the quest to deliver passenger from bar to city
        if event.option_id == 'passenger_from_bar_to_city_delivered':
            self.show_location('Brackenbridge')
            return

        # Finish the quest to deliver passenger from mine to bar
        if event.option_id == 'passenger_from_mine_to_bar_delivered':
            self.show_location('The Stingray Bar')
            return

        # Refuse to give the policeman a ride to town
        if event.option_id == 'refuse_passenger':
            self.show_location('Marshal')
            return

        # Refuse to give the passenger a ride from mine to city
        if event.option_id == 'refuse_passenger_from_mine_to_city':
            self.show_location('Mining Settlement')
            return

        # Refuse to give the passenger a ride from city to mine
        if event.option_id == 'refuse_passenger_from_city_to_mine':
            self.show_location('Brackenbridge')
            return

        # Refuse to give the passenger a ride from bar to city
        if event.option_id == 'refuse_passenger_from_bar_to_city':
            self.show_location('The Stingray Bar')
            return

        # Refuse to give the passenger a ride from mine to bar
        if event.option_id == 'refuse_passenger_from_mine_to_bar':
            self.show_location('Mining Settlement')
            return

        # Start policeman delivering quest
        if event.option_id == 'take_policeman':
            self.engine.take_policeman({})
            self.show_location('Marshal')
            return

        # Start passenger delivering from the mine to the city
        if event.option_id == 'take_passenger_from_mine_to_city':
            self.engine.take_passenger_from_mine_to_city({})
            self.show_location('Mining Settlement')
            return

        # Start passenger delivering from the city to mine
        if event.option_id == 'take_passenger_from_city_to_mine':
            self.engine.take_passenger_from_city_to_mine({})
            self.show_location('Brackenbridge')
            return

        # Start passenger delivering from bar to city
        if event.option_id == 'take_passenger_from_bar_to_city':
            self.engine.take_passenger_from_bar_to_city({})
            self.show_location('The Stingray Bar')
            return

        # Start passenger delivering from mine to bar
        if event.option_id == 'take_passenger_from_mine_to_bar':
            self.engine.take_passenger_from_mine_to_bar({})
            self.show_location('Mining Settlement')
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

        # Take a policeman to the city (there should be no other passengers)
        # The likelihood that a policeman will ask for a ride is 10%
        if self.state.world.current_location == "Marshal" and event.option_id == 'back_crossroads':
            if not self.state.truck.passenger:
                if random.random() < 0.1:
                    self.quest_text.update(
                        'Your truck was slowly moving onto the road when you heard a knock on '
                        'the cab window. It was one of the marshal’s men.'
                        '– I [green]need to get to Brackenbridge[/green] on business. '
                        'Can you give me a ride? – he asked. “I don’t have money, '
                        'but I can pay with something else… '
                        'If you take me, you’ll get [green]8 shells[/green].'
                    )
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Sure', 'take_policeman'))
                    self.command_panel.add_option(Option('I have more important things to do', 'refuse_passenger'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Policeman delivery quest completion
        if self.state.world.current_location == 'Brackenbridge':
            if 'policeman' in self.state.truck.passenger:
                self.quest_text.update(
                    'When you stopped at the city square, the marshal’s man jumped out of the cab.\n'
                    '– Thanks for the ride, brother. You really helped me out, – he said, '
                    'handing you a small box.\n'
                    'Inside were [green]8 shotgun shells[/green].\n'
                    '– Use them well!'
                )
                self.engine.policeman_delivered()
                self.command_panel.clear_options()
                self.command_panel.add_option(Option('Next', 'policeman_delivered'))
                self.set_focus(self.command_panel)
                self.command_panel.highlighted = 0
                return

        # Take randomly passenger from mine to the city (there should be no other passengers)
        # The likelihood that randomly passenger will ask for a ride is 15%
        if self.state.world.current_location == "Mining Settlement" and event.option_id == 'back_to_road':
            if not self.state.truck.passenger:
                if random.random() < 0.15:
                    self.quest_text.update(
                        'You were about to leave when a dirty miner ran up to your window.\n'
                        '– Hey, boss! Can you give me a [green]lift to Brackenbridge?[/green] '
                        'I’ll pay 40 credits!'
                    )
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Sure',
                                                         'take_passenger_from_mine_to_city'))
                    self.command_panel.add_option(
                        Option('I have more important things to do',
                               'refuse_passenger_from_mine_to_city'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Passenger from mine to the city delivery quest completion
        if self.state.world.current_location == 'Brackenbridge':
            if 'passenger' in self.state.truck.passenger:
                if self.state.truck.passenger['passenger'] == ('Mining Settlement', 'Brackenbridge'):
                    self.quest_text.update(
                        '– Finally home! – your passenger said when you arrived. '
                        'He handed you [green]40 credits[/green] and disappeared into an alley.'
                    )
                    self.engine.passenger_from_mine_to_city_delivered()
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Next',
                                                         'passenger_from_mine_to_city_delivered'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Take randomly passenger from city to mine (there should be no other passengers)
        # The likelihood that randomly passenger will ask for a ride is 15%
        if self.state.world.current_location == "Brackenbridge" and event.option_id == 'back_to_road':
            if not self.state.truck.passenger:
                if random.random() < 0.15:
                    self.quest_text.update(
                        'Just as you were about to leave, a young boy ran up to your truck.\n'
                        '– Hey, friend! Are you [green]heading to the mines[/green]? I heard I can make '
                        'lots of money there. Where there’s money, I must be! '
                        'I’ll pay [green]30 credits[/green] for the ride!'
                    )
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Sure',
                                                         'take_passenger_from_city_to_mine'))
                    self.command_panel.add_option(
                        Option('I have more important things to do',
                               'refuse_passenger_from_city_to_mine'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Passenger from city to mine delivery quest completion
        if self.state.world.current_location == 'Mining Settlement':
            if 'passenger' in self.state.truck.passenger:
                if self.state.truck.passenger['passenger'] == ('Brackenbridge', 'Mining Settlement'):
                    self.quest_text.update(
                        '– Yeah, baby! Soon I’ll be rich! – the boy shouted, '
                        'jumping out when you arrived.\n'
                        '– Here, take your [green]30 credits[/green]. And don’t forget to drink a '
                        'cup of wine or two to my success!'
                    )
                    self.engine.passenger_from_city_to_mine_delivered()
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Next',
                                                         'passenger_from_city_to_mine_delivered'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Take randomly passenger from bar to city (there should be no other passengers)
        # The likelihood that randomly passenger will ask for a ride is 15%
        if self.state.world.current_location == "The Stingray Bar" and event.option_id == 'back_to_road':
            if not self.state.truck.passenger:
                if random.random() < 0.15:
                    self.quest_text.update(
                        'Just as you started the engine, a very drunk man climbed into your truck.\n'
                        '– Drive on, driver. [green]Next stop – Brackenbridge[/green]. I’ll pay you '
                        '[green]100 credits[/green], no problem!'
                    )
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Sure',
                                                         'take_passenger_from_bar_to_city'))
                    self.command_panel.add_option(
                        Option('I have more important things to do',
                               'refuse_passenger_from_bar_to_city'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Passenger from bar to city delivery quest completion
        if self.state.world.current_location == 'Brackenbridge':
            if 'passenger' in self.state.truck.passenger:
                if self.state.truck.passenger['passenger'] == ('The Stingray Bar', 'Brackenbridge'):
                    self.quest_text.update(
                        'Ah, travelers… the fun goes on. Time to spend my money in Brackenbridge.\n'
                        '– Here, [green]take your 100 credits[/green], – he said, handing you the money.\n'
                        'Then he slammed the door and staggered away.'
                    )
                    self.engine.passenger_from_bar_to_city_delivered()
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Next',
                                                         'passenger_from_bar_to_city_delivered'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Take randomly passenger from mine to bar (there should be no other passengers)
        # The likelihood that randomly passenger will ask for a ride is 15%
        if self.state.world.current_location == "Mining Settlement" and event.option_id == 'back_to_road':
            if not self.state.truck.passenger:
                if random.random() < 0.15:
                    self.quest_text.update(
                        'You started the engine and headed for the exit, but near '
                        'the gate you saw someone waving and slowed down. '
                        'A strong miner ran up to your window.\n'
                        '– Hey, driver! I’m off to spend my hard-earned money. '
                        'Give me a [green]ride to the Stingray bar[/green]. '
                        'I’ll pay [green]60 credits[/green].'
                    )
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Sure',
                                                         'take_passenger_from_mine_to_bar'))
                    self.command_panel.add_option(
                        Option('I have more important things to do',
                               'refuse_passenger_from_mine_to_bar'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                    return

        # Passenger from mine to bar delivery quest completion
        if self.state.world.current_location == 'The Stingray Bar':
            if 'passenger' in self.state.truck.passenger:
                if self.state.truck.passenger['passenger'] == ('Mining Settlement', 'The Stingray Bar'):
                    self.quest_text.update(
                        '– Thanks, brother! You saved me, – the miner said, handing you '
                        '[green]60 credits[/green] before walking toward the bar with a dancing step.'
                    )
                    self.engine.passenger_from_mine_to_bar_delivered()
                    self.command_panel.clear_options()
                    self.command_panel.add_option(Option('Next',
                                                         'passenger_from_mine_to_bar_delivered'))
                    self.set_focus(self.command_panel)
                    self.command_panel.highlighted = 0
                return

        # Drox delivery quest completion
        if self.state.world.current_location == 'Brackenbridge':
            if 'drox' in self.state.truck.passenger:
                self.quest_text.update(
                    f'You stopped in the city square and tried to wake up the drox. '
                    f'He didn’t wake at first, so you shook him for five minutes until he opened his eyes.\n'
                    f'– What? What is it? – he asked sleepily.\n'
                    f'– We\'re here!'
                    f'– Really? Thanks, brother. I came to work at the factory now, '
                    f'no more wild life for me. So take my trophy [green]shotgun and 6 shells[/green] '
                    f'— it may help you.\n'
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
            destination = option['goto']
            # When there is a random encounter on the road,
            # record the initial destination of the journey.
            if destination == 'next':
                destination = self.state.world.next_location
                self.state.world.next_location = None
            # Check if a random meeting can generate
            # and if there isn't already have an active meeting
            encounter_event = self.engine.randomize_encounter_on_road()
            if encounter_event and not self.state.world.active_encounter:
                self.state.world.next_location = destination
                self.show_location(encounter_event)
                self.state.world.active_encounter = True
                return

            self.show_location(destination)
            # Reset flags of active encounter after the meeting is over
            self.state.world.active_encounter = False
            self.state.world.next_location = None
            self.state.invisible_options.discard('ask_about_news')
            self.state.invisible_options.discard('ask_about_fuel')

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
                f'– We currently have [green]{self.state.world.corn_farm.offer} tonnes[/green] '
                'of corn, packed in barrels, one tonne each. '
                f'We sell them for [green]{self.state.world.corn_farm.price} credits per barrel[/green]. '
                'And if you want to sell something yourself, sorry, '
                'we\'re not buying anything. We have everything we need.'
            )

        if option_name.startswith('buy_corn'):
            return (
                f'– We currently have [green]{self.state.world.corn_farm.offer} tonnes[/green] '
                'of corn, packed in barrels, one tonne each. '
                f'We sell them for [green]{self.state.world.corn_farm.price} credits per barrel[/green]. '
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
                '\"[green]Fried meat with mushrooms – 6 credits[/green]. '
                '[green]A bed for 6 hours – 10 credits (for Stingrays: 5 credits)[/green]\"'
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
                    f'– So, here the repair will cost [green]{self.engine.bolt_repair_cost()}[/green] credits. '
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
                    'you saw that someone [green]had stolen a few credits[/green] '
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
                    'You got up, kicked one in the legs, broke another\'s nose, '
                    'and the gang ran off. You [green]were hurt[/green] too. '
                    'Better not to walk here at twilight – it’s their time.'
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
                    'handing you the menu.\nYou quickly looked through the options, '
                    'noting what you could afford and what was too expensive.'
                )
            else:
                return (
                    'A sign hangs on the door:\n'
                    '\"[green]Closed[/green].\n'
                    'The restaurant is open daily:\n'
                    '[green]from 9:00 until the last guest after 23:59[/green].\"'
                )

        # Dynamic quest text depending on the quantity and price of scrap
        if option_name == 'go_wreckyard':
            return (
                'The vehicle skillfully entered the scrapyard. You were about to '
                'delve deeper into the trash maze, but a three-meter-tall robot blocked '
                'your way. Rusty as it was, it looked impressive…\n\n'
                '– You’re in the Varnock brothers’ territory, gringo! – said the man '
                'inside the robot. – If you’re here on business, know this: we '
                f'currently have [green]{self.state.world.wreckyard.offer} tons[/green] '
                f'of scrap metal. '
                f'[green]{self.state.world.wreckyard.price} credits per ton[/green]. '
                'The scrap is pressed and neatly packed—top quality stuff.'
            )

        if option_name.startswith('buy_scrap'):
            return (
                '– If you’re here on business, know this: we '
                f'currently have [green]{self.state.world.wreckyard.offer} tons[/green] of scrap metal. '
                f'[green]{self.state.world.wreckyard.price} credits per ton[/green]. '
                'The scrap is pressed and neatly packed—top quality stuff.'
            )

        # Hero swims in forrest lake
        if option_name == 'swim_more':
            if self.state.hero.swims_qty == 3 and self.state.hero.health <= 40:
                return (
                    'You kept swimming in the lake when suddenly you [green]felt energy[/green] '
                    'filling your body and your [green]wounds healing[/green]. Looks like '
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
                    'You swam in the water for [green]five minutes.[/green] In such water, '
                    'it didn’t give you much pleasure. Only made you [green]feel more tired[/green].'
                )

        # Dynamic quest text depending on the quantity and price of scrap
        if option_name == 'go_to_trading_house' or option_name.startswith('buy_coal'):
            return (
                'You are in a room full of coal bags. A man in a helmet sits on '
                'a small chair near the door.\n'
                f'– Here\'s the deal. We sell coal for [green]{self.state.world.mine.price} '
                'credits per ton[/green]. The coal is clean and ready to use, so no problems. '
                f'Right now, we have [green]{self.state.world.mine.offer} tons[/green] of coal in stock.'
                'Also, we buy food. Especially [green]corn. We pay 45 credits per ton[/green]. '
                'Miners eat corn with great appetite!'
            )

        # Dynamic quest text depending on the quantity of mined coal
        if option_name == 'work_in_mine':
            earned_money = self.engine.work_in_mine()
            text = (
                '– That’s it! One hour is over, – the huge miner shouted behind you. '
                'He wrote your name on the bag, put it on the lift, and said:\n'
                '– Go upstairs for your pay. '
                'At the mine exit, a dirty man with a notebook was already waiting.\n'
            )
            if earned_money == 3:
                text += '– I weighed the bag. About one and a half tons. Good! You [green]earned 3 credits[/green].'
            elif earned_money == 2:
                text += '– I weighed the bag. About one ton. Good! You [green]earned 2 credits[/green].'
            elif earned_money == 0:
                text = (
                    'You were calmly mining coal when suddenly a pile of rocks fell '
                    'from above. The miners rushed to dig you out…\n'
                    'You woke up outside. Your body hurt — the rockfall [green]hit you hard[/green].\n'
                    'But hooray! You managed to stand up. Even better, nothing was '
                    'broken. Looks like you got away quite lightly…'
                )

            return text

        # Dynamic quest text depending on the quantity of mined coal
        if option_name == 'about_fixing':
            return (
                'Go to the garage. Dex will check your wreck, – the woman said.\n'
                'In a moment, the garage doors lifted, and you drove inside. '
                'The place was full of metal junk—mufflers, engines, tanks, springs. '
                'Among it all worked a man in coveralls. That must be Dex.\n'
                '– Let’s see, – the mechanic said, checking your vehicle.\n'
                f'– Well, – he concluded, – that’s [green]{self.engine.dex_repair_cost()} '
                'credits[/green] of work. Are you paying?'
            )

        # Dynamic quest text for buying porridge in mining settlement
        # depending on the hanger level
        if option_name == 'buy_porridge' and self.state.hero.hanger >= 39:
            return (
                'The drox took the money, pressed a lever on some machine, '
                'and half a minute later the device spat out a portion of brown mush. '
                'Dropping THIS onto a plate, the drox stuck a metal spoon in and handed '
                'it to you.\n'
                '– Bring the dish back, – he muttered.\n'
                'You nodded.\n'
                'The taste was even worse than the look. You managed a couple of spoons, '
                'but with each one it was harder to fight the urge to vomit. '
                'Finally, your stomach rebelled, and you threw up. '
                'Seems you weren’t [green]hungry enough[/green] to finish that yellow substance.'
            )
        if option_name == "buy_porridge":
            return (
                'The drox took your money, pulled a lever on the machine, '
                'and soon it gave out some green mush. It tasted worse than it looked. '
                'But you were too hungry, so you ate it all, trying not to throw up.'
            )

        # Dynamic quest text for dealer on the road
        if self.state.world.current_location == "Road - healer":
            text = (
                '– Hind legs of the critter, soaked in milk. '
                '[green]Heals wounds. 30 credits[/green].\n'
                '– Raw eye of an arthropod. Clears the mind, [green]gives strong energy[/green], '
                'and cleans toxins, causing vomiting. Only [green]15 credits[/green].\n'
                '– Frog skin broth with sour cilantro sauce. [green]Fills hunger[/green] and '
                'raises endurance. [green]20 credits[/green].\n'
                '- Dead jug-fly. [green]Boosts male power[/green] to the third chi sphere. '
                'One fly – [green]5 credits[/green].'
            )
            if option_name == 'stop':
                return (
                    'You quickly pulled your truck to the side, but the wheel-baobab car '
                    'bounced toward you for a while. Finally, it stopped next to your '
                    'vehicle, puffing black smoke from its exhaust. The door opened, '
                    'and a thin old man approached your window—bald.\n'
                    '– I bring nirvana to this gray world, – the old man said in '
                    'a trembling voice. – Your eyes show weariness from something dark and'
                    ' vast. I think my remedies will help you:\n'
                    ) + text
            elif option_name == 'buy_legs':
                text = (
                        'The legs turned out to be quite tasty. '
                        'Suddenly you started shaking, and you felt your [green]wounds slowly closing[/green].'
                        '– Anything else? – the old man asked.\n'
                        'You tried to recall what other remedies he had mentioned. '
                        'The list went something like this:\n'
                       ) + text
            elif option_name == 'buy_eye':
                text = (
                        'The healer pulled a huge bluish eye from a three-liter jar.'
                        'Without thinking too much, you grabbed it and swallowed it in one go. '
                        'The eye burst in your mouth, spreading bitter liquid across your tongue...\n'
                        'In the window you saw the healer’s satisfied face. '
                        'You stood up, feeling [green]incredible energy[/green], though now your head '
                        'hurt badly and your bones ached.'
                        '– Anything else? – the old man asked.\n'
                        'You tried to recall what other remedies he had mentioned. '
                        'The list went something like this:\n'
                       ) + text
            elif option_name == 'buy_broth':
                text = (
                        'The broth was very thick, and you had to drink it slowly. '
                        'But it [green]filled you well[/green] and gave '
                        'you [green]extra energy[/green].\n'
                        '– Anything else? – the old man asked.\n'
                        'You tried to recall what other remedies he had listed. '
                        'The list went something like this:\n'
                       ) + text
            elif option_name == 'buy_fly':
                text = (
                        'You ate the fly but [green]felt nothing[/green].\n'
                        'What did you give me?!” you shouted angrily.\n'
                        '– What did you expect, driver? – the healer replied. – The male '
                        'chi power does not show up instantly. It needs the right situation, '
                        'you understand?'
                        'Well, that sounded convincing enough. Only one way to '
                        'test his words in practice.'
                        '– Anything else? – the old man asked.'
                       ) + text
            return text

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
            for passang, info in truck.passenger.items():
                truck_state += f'{passang} to {info[1]}'

        if world.biker_mood != None and world.biker_mood <= 4:
            biker_mood = world.biker_mood
            truck_state += f'\n{
            ('Biker looks determined', 'Biker is confident', 'Biker is careful',
             'Biker is afraid', 'Biker is afraid')[biker_mood]}'

        self.state_panel_widget.update(world_state + hero_state + truck_state)
