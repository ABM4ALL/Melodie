# import cython
#
# # try:
# from cython.cimports.Melodie.boost.grid import GridAgent
# # except:
# #     from Melodie import GridAgent
#
#
# @cython.cclass
# class CovidAgent(GridAgent):
#     condition = cython.declare(cython.int, visibility='public')
#
#     def setup(self):
#         self.x = 0
#         self.y = 0
#         self.category = 0
#         self.condition = 0
#
#     @cython.ccall
#     def move(self):
#         self.rand_move(1, 1)
