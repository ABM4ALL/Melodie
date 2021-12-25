# # def binary_search(lis, num):
# #     left = 0
# #     right = len(lis) - 1
# #     mid = 0
# #     while left <= right:  # 循环条件
# #         mid = (left + right) // 2  # 获取中间位置，数字的索引（序列前提是有序的）
# #         # print(lis[0])
# #         if num < lis[mid][0]:  # 如果查询数字比中间数字小，那就去二分后的左边找，
# #             right = mid - 1  # 来到左边后，需要将右变的边界换为mid-1
# #         elif num > lis[mid][0]:  # 如果查询数字比中间数字大，那么去二分后的右边找
# #             left = mid + 1  # 来到右边后，需要将左边的边界换为mid+1
# #         else:
# #             return mid  # 如果查询数字刚好为中间值，返回该值得索引
# #
# #     if mid == 0:
# #         return 0
# #     else:
# #         return -1  # 如果循环结束，左边大于了右边，代表没有找到
#
# import numpy as np
# import random
#
#
# class GeneticAlgorithm:
#
#     def translate_binary2real(self, binary_array, min_value, max_value):
#         sum = 0
#         length = len(binary_array)
#         real_maximum = 2 ** length - 1
#         for bit in range(0, length):
#             sum += binary_array[bit] * 2 ** (length - 1 - bit)
#         real_value = min_value + sum / real_maximum * (max_value - min_value)
#         return real_value
#
#     def prob_calculation(self, fitness_array):
#
#         fitness_max = fitness_array.max()
#         fitness_min = fitness_array.min()
#         score_array = (fitness_array - fitness_min) / (fitness_max - fitness_min)
#         score_sum = score_array.sum()
#         prob_array = score_array / score_sum
#
#         return prob_array
#
#     def gene_pick(self, prob_array, strategy_population):
#
#         random_number = random.uniform(0, 1)
#         accumulated_pick_probability = 0
#
#         for strategy in range(0, strategy_population):
#
#             accumulated_pick_probability += prob_array[strategy]
#             if accumulated_pick_probability >= random_number:
#                 gene_picked_number = strategy
#                 break
#             else:
#                 gene_picked_number = np.random.randint(strategy_population)
#
#         return gene_picked_number
#
#     def crossover(self, gene_1, gene_2, probability_1, probability_2):
#
#         probability = probability_1 / (probability_1 + probability_2)
#         gene_new = np.zeros((len(gene_1),))
#
#         for bit in range(0, len(gene_1)):
#             random_number = random.uniform(0, 1)
#             if random_number <= probability:
#                 gene_new[bit] = gene_1[bit]
#             else:
#                 gene_new[bit] = gene_2[bit]
#
#         return gene_new
#
#     def mutation(self, gene, mutation_prob):
#
#         random_number = random.uniform(0, 1)
#         if random_number <= mutation_prob:
#             randint = random.randint(0, len(gene) - 1)
#             if gene[randint] == 0:
#                 gene[randint] = 1
#             else:
#                 gene[randint] = 0
#         else:
#             pass
#
#         return gene
#
#     def population_update(self, population, fitness_array, mutation_prob, population_scale):
#
#         mutation_prob = mutation_prob
#         strategy_population = population_scale
#
#         prob_array = self.prob_calculation(fitness_array)
#         population_new = np.zeros(population.shape)
#         strategy_number_list = [i for i in range(0, strategy_population)]
#         random.shuffle(strategy_number_list)
#
#         for strategy in range(0, strategy_population):
#             gene_1_number = self.gene_pick(prob_array, strategy_population)
#             gene_2_number = self.gene_pick(prob_array, strategy_population)
#             gene_1 = population[gene_1_number]
#             gene_2 = population[gene_2_number]
#
#             gene_new = self.crossover(gene_1,
#                                       gene_2,
#                                       prob_array[gene_1_number],
#                                       prob_array[gene_2_number])
#
#             gene_new = self.mutation(gene_new, mutation_prob)
#
#             population_new[strategy_number_list[strategy]] = gene_new
#
#         return population_new
#
#     pass
#
#
# if __name__ == "__main__":
#
#     def loss_function(x):
#         y_target = 10
#         y_x = 3 * x + 1
#         return abs(y_target - y_x)  # solution: x = 3
#
#
#     def fitness_function(loss):
#         # 就是为了把loss变成“正向/越大越好”的fitness，没有直接用1/loss而是求2**loss，是为了避免loss等于0报错
#         return 1 / 2 ** loss
#
#
#     training_generation = 100
#     strategy_population_size = 100
#     mutation_prob = 0.02  # 突变为了避免收敛到局部最优，但太大的导致搜索不稳定
#     strategy_param_code_length = 20  # 这个值越大解的精度越高 --> 把下面区间[strategy_param_min, strategy_param_max]分得越细
#     strategy_param_min = 0
#     strategy_param_max = 10
#     GA = GeneticAlgorithm()
#
#     strategy_population = np.random.randint(2, size=(strategy_population_size, strategy_param_code_length))
#     for gen in range(0, training_generation):
#         strategy_fitness = np.zeros((strategy_population_size,))
#         x_sum = 0
#         for i, strategy in enumerate(strategy_population):
#             x = GA.translate_binary2real(strategy, strategy_param_min, strategy_param_max)
#             x_sum += x
#             strategy_fitness[i] = fitness_function(loss_function(x))
#         print("x_average_value_current_generation = " + str(round(x_sum / strategy_population_size, 3)))
#         strategy_population = GA.population_update(strategy_population, strategy_fitness,
#                                                    mutation_prob, strategy_population_size)
