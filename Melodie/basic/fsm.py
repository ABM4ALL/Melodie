from typing import Dict, Set


class FSM:
    def __init__(self, initial_state: int, state_transition_table: Dict[int, Set[int]]):
        self.current_state: int = initial_state
        self.stt = state_transition_table

    def state_change(self, new_state: int):
        assert new_state in self.stt.keys()
        assert new_state in self.stt[self.current_state], (new_state, self.current_state, self.stt[self.current_state])
        self.current_state = new_state
