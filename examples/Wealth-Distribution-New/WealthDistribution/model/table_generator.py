# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
import random

import numpy as np

from Melodie.table_generator import TableGenerator

logger = logging.getLogger(__name__)


class GiniTableGenerator(TableGenerator):

    def setup(self):
        # TODO 多参数之间的关系.改成set_agent_params.

        self.add_agent_param('productivity', self.scenario.agent_productivity)
        self.add_agent_param('account', lambda: float(np.random.randint(self.scenario.agent_account_min,
                                                                        self.scenario.agent_account_max)))

