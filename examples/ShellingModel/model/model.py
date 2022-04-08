from Melodie import Model, Grid, Spot, AgentList
from .agent import ShellingModelAgentTypeA, ShellingModelAgentTypeB
from .data_collector import ShellingModelDataCollector
from .environment import ShellingModelEnvironment


class ShellingModelModel(Model):

    def setup(self):
        with self.define_basic_components():
            self.data_collector = ShellingModelDataCollector()
            self.environment = ShellingModelEnvironment()
            self.agent_list_a: AgentList[ShellingModelAgentTypeA] = \
                self.create_agent_container(ShellingModelAgentTypeA, 160)
            self.agent_list_b: AgentList[ShellingModelAgentTypeB] = \
                self.create_agent_container(ShellingModelAgentTypeB, 160)
        self.grid = Grid(Spot, 20, 20, multi=False)
        self.grid.add_agent_container(ShellingModelAgentTypeA.category, self.agent_list_a, "random_single")
        self.grid.add_agent_container(ShellingModelAgentTypeB.category, self.agent_list_b, "random_single")

    def run(self):
        for i in self.routine():

            unsatisfied_a, unsatisfied_b = self.environment.calc_satisfactory(self.grid, self.agent_list_a,
                                                                              self.agent_list_b)
            self.environment.unsatisfied_move_to_empty(unsatisfied_a, self.agent_list_a, self.grid)
            self.environment.unsatisfied_move_to_empty(unsatisfied_b, self.agent_list_b, self.grid)
            # for a_id in unsatisfied_a:
            #     pos = self.grid.find_empty_spot()
            #     agent_a = self.agent_list_a.get_agent(a_id)
            #
            #     self.grid.move_agent(agent_a, agent_a.category, pos[0], pos[1])
            #     agent_a.x = pos[0]
            #     agent_a.y = pos[1]
            #
            # for b_id in unsatisfied_b:
            #     pos = self.grid.find_empty_spot()
            #     agent_b = self.agent_list_b.get_agent(b_id)
            #
            #     self.grid.move_agent(agent_b, agent_b.category, pos[0], pos[1])
            #     agent_b.x = pos[0]
            #     agent_b.y = pos[1]

            # print(
            #     [(self.agent_list_a.get_agent(a_id).x, self.agent_list_a.get_agent(a_id).y) for a_id in unsatisfied_a],
            #     unsatisfied_b)
            #
            # for y in range(20):
            #     for x in range(20):
            #
            #         agents = self.grid.get_agent_ids(x, y)
            #         if len(agents) == 0:
            #             print("-", end="")
            #         elif agents[0][1] == 0:
            #             print("o", end="")
            #         elif agents[0][1] == 1:
            #             print('x', end="")
            #     print("\n", end="")
            # print(i, len(unsatisfied_b) + len(unsatisfied_a), "=======" * 20)
