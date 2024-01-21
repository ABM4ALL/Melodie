# -*- coding:utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
print(os.path.abspath(sys.path[0]))
import base
from new_trainer_algorithm import *


# @pytest.mark.timeout(30)
def test_chrom_params_algorithm():
    params = GATrainerParams(
        0, 5, 20, 20, 0.02, 20, param1_min=-1, param1_max=1, param2_min=-1, param2_max=1
    )
    mgr = MockTrainer(cfg_for_trainer, Scenario, NewModel, DFLoader, 4)
    mgr.setup()
    mgr.pre_run()
    ta = GATrainerAlgorithm(params, mgr)
    scenario = Scenario(0)
    meta = GATrainerAlgorithmMeta()
    mgr.pre_run()
    ta.run(scenario, meta)
    ta.stop()

if __name__ == "__main__":
    test_chrom_params_algorithm()