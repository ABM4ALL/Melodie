# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging

import numpy as np

from Melodie.table_generator import TableGenerator

logger = logging.getLogger(__name__)


class GiniTableGenerator(TableGenerator):

    def setup(self):
        self.add_agent_param('productivity', self.scenario.agent_productivity)
        self.add_agent_param('account', lambda: float(np.random.randint(self.scenario.agent_account_min,
                                                                        self.scenario.agent_account_max)))
