from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Melodie.Agent import Agent


class MelodieException(Exception):
    def __init__(self, exc_id: int, text: str):
        super(MelodieException, self).__init__(text)
        self.id = exc_id


class MelodieExceptions:
    class State:
        ID = 1100

        @staticmethod
        def StateNotFoundError(state, all_states):
            return MelodieException(1101,
                                    f'State {repr(state)} is not defined. All states are: {all_states}')

        @staticmethod
        def CannotMoveToNewStateError(old_state, new_state, all_possible_new_states: set):
            if len(list(all_possible_new_states)) == 0:
                return MelodieException(1102,
                                        f'Current state is {repr(old_state)}, on which the status could only move to'
                                        f' itself. However the new state was {repr(new_state)}')
            else:
                return MelodieException(1102,
                                        f'Current state is {repr(old_state)}, on which the status could only move to'
                                        f' {all_possible_new_states}. However the new state was {repr(new_state)}')
