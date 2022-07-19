from Melodie import GATrainerParams
from .testsko import MyGA
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Melodie import AgentList


class AlgorithmInterface:
    def __init__(self, algo_type: str, agent_container: "AgentList", updater, target_fcn, params: GATrainerParams):
        self.type = algo_type
        self.values = {}
        assert self.type in {"ga"}
        lower_bounds = [p.min for p in params.parameters]
        upper_bounds = [p.max for p in params.parameters]

        def f(a):
            def f_inner(p):
                print(p)
                return target_fcn(a)

            return f_inner

        self.algorithms = [MyGA(f(a),
                                len(params.parameters),
                                size_pop=params.strategy_population,
                                max_iter=params.number_of_generation,
                                prob_mut=params.mutation_prob,
                                lb=lower_bounds,
                                ub=upper_bounds,
                                precision=0.5 ** (params.strategy_param_code_length)
                                ) for a in agent_container]
        print(self.algorithms[0].lb, self.algorithms[0].ub)
        self.updater = updater

    def run_one_step(self):
        for algo in self.algorithms:
            algo.run(1)
