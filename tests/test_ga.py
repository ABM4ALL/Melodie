import numpy as np

from Melodie import Scenario
from Melodie.algorithms.ga import translate_binary2real, prob_calculation, gene_pick, crossover, mutation, \
    population_update, GeneticAlgorithmTrainer


# def test_translate_binary_to_real():
#     real = translate_binary2real([1, 1, 1, 1, 1], 0, 1)
#
#     assert real == 1.0
#     real = translate_binary2real([0, 0, 0, 0, 0], 0, 1)
#
#     assert real == 0.0
from tests._trainer import _callable_f


def test_prob_calc():
    score = (np.array([1, 2, 3, 4, 5]) - 1) / (5 - 1)
    score_sum = score.sum()
    probs = score / score_sum

    probs_ret = prob_calculation(np.array([1, 2, 3, 4, 5]))
    assert tuple(probs_ret) == tuple(probs)


def test_gene_pick():
    ret = gene_pick(np.array([0, 0, 0.2, 0.8]), 4)
    assert ret in {2, 3}


def test_crossover():
    gene1 = np.array([0, 1, 0, 0, 1])
    gene2 = np.array([1, 0, 1, 0, 1])
    gene_new = crossover(gene1, gene2, 1, 0)
    print(gene_new)
    for i in range(len(gene_new)):
        assert gene_new[i] == gene1[i]

    gene1 = np.array([0, 1, 0, 0, 1])
    gene2 = np.array([1, 0, 1, 0, 1])
    gene_new = crossover(gene1, gene2, 0, 1)
    print(gene_new)
    for i in range(len(gene_new)):
        assert gene_new[i] == gene2[i]


def test_mutation():
    for i in range(10):
        arr = np.array([0, 1, 0, 1, 0, 1])
        ret = mutation(arr, 1)
        for i in ret:
            assert ret[i] in {0, 1}

        ret = mutation(arr, 0)
        for i in ret:
            assert ret[i] == arr[i]


def test_population_update():
    population = np.array([
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1]
    ])
    fitness_array = np.array([0.0, 0.0, 0.0, 1.0])
    mutation_prob = 0
    population_scale = len(population)
    new = population_update(population, fitness_array, mutation_prob, population_scale)
    for i in range(4):
        tuple(new[i]) == (0, 0, 0, 1, 1)





def test_ga4trainer():
    agent_num = 5
    scenario = Scenario()
    trainer_algorithm = GeneticAlgorithmTrainer(10, 10, 0.02, 5)
    trainer_algorithm.set_parameters_agents(agent_num, 2, ['param_a', 'param_b'], ['result_value'], [])
    opt = trainer_algorithm.optimize_multi_agents(_callable_f, scenario)
    strategy_population, params, fitness, meta = opt.__next__()
