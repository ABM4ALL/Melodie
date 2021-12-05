
class AbstractTrainer:
    # 用来individually calibrate agents' parameters，
    # 只考虑针对strategy中参数的off-line learning。online-learning的部分千奇百怪，暂时交给用户自己来吧。
    pass

class GeneticAlgorithmTrainer(AbstractTrainer):
    pass

class ParticleOptimizationTrainer(AbstractTrainer):
    pass
