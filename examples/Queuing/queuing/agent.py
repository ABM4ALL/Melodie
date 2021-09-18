import random

from Melodie.Agent import Agent

from Melodie.Model import Model
from Melodie.AgentManager import AgentManager


class Customer(Agent):
    def setup(self):
        self.service_minutes = random.randint(5, 5)
        self.patience = random.randint(30, 60)
        self.status = 'waiting'  # waiting, serving, satisfied, unsatisfied
        self.service_ready = False  # If his

    @Agent.state_transition("status", ('waiting', 'serving'))
    def service_started(self):
        return self.service_ready

    @Agent.state_transition("status", ("serving", "serving"))
    def serve(self):
        self.service_minutes -= 1
        return self.service_minutes > 0

    @Agent.state_transition("status", ("waiting", "waiting"))
    def wait(self):
        self.patience -= 1
        return (self.patience > 0) and (not self.service_ready)
        # return True

    @Agent.state_transition('status', ('serving', 'satisfied'))
    def service_finished(self):
        return self.service_minutes <= 0

    @Agent.state_transition('status', ('waiting', 'unsatisfied'))
    def quit_waiting(self):
        return (self.patience <= 0) and (not self.service_ready)

    def step(self):
        current_state = self.status
        possible_next_states = self._state_watch['status'][self.status]
        performed_transitions = []
        for next_state in possible_next_states:
            transition = (current_state, next_state)
            # print(self._state_funcs['status'][transition],transition)

            if self._state_funcs['status'][transition](self):
                performed_transitions.append(transition)
                if len(performed_transitions) > 1:
                    raise ValueError(f'Error transitions {performed_transitions} might have overlapping conditions.')
                self.status = transition[1]

                # break


class WaitingModel(Model):
    def __init__(self, agent_class):
        self.queue_len = 10
        self.agent_manager = AgentManager(agent_class, 0)

    def new_agent(self) -> bool:
        # print(len(self.agent_manager))
        if len(self.agent_manager) < self.queue_len:
            agent = Customer(self.agent_manager)
            agent.setup()
            self.agent_manager.add(agent)
            return True
        return False

    def run(self):
        satisfied_count = 0
        unsatisfied_count = 0
        gaveup_count = 0  # gave up because queue was too long
        for i in range(10000):
            # print(f"step: {i} ;", end='')
            if random.random() < 0.2:
                succeeded = self.new_agent()
                if not succeeded:
                    gaveup_count += 1
            if len(self.agent_manager.agents) <= 0:
                continue
            else:
                first_agent = self.agent_manager.agents[0]
                # return
                # print(first_agent._state_funcs)
                # print(first_agent._state_watch)

                if first_agent.current_state_is('status', 'waiting'):
                    first_agent.service_ready = True
                elif first_agent.current_state_is("status", 'satisfied'):
                    self.agent_manager.remove(first_agent)
                    satisfied_count += 1
                elif first_agent.current_state_is("status", 'unsatisfied'):
                    self.agent_manager.remove(first_agent)
                    unsatisfied_count += 1
            for agent in self.agent_manager.agents:
                agent.step()
            #     print(f"<{agent.status},  {agent.patience} {agent.service_minutes}>", end='  ')
            # print("\n")
        print(unsatisfied_count, satisfied_count, gaveup_count)


if __name__ == "__main__":
    model = WaitingModel(Customer)

    model.run()
    # c = Customer(model.agent_manager)
    # c.plot_md()
