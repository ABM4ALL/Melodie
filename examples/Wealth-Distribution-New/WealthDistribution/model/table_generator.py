# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
from typing import ClassVar

import numpy as np
import pandas as pd
import pandas.io.sql

from Melodie.config import CONN
from Melodie.table_generator import TableGenerator
from .scenario import GiniScenario
from Melodie.db import DB
from Melodie.agent import Agent

logger = logging.getLogger(__name__)


class GiniTableGenerator(TableGenerator):

    def setup(self):
        self.scenario: GiniScenario = self.scenario
        self.add_agent_param('productivity', self.scenario.agent_productivity)
        self.add_agent_param('account', lambda: np.random.randint(self.scenario.agent_account_min,
                                                                  self.scenario.agent_account_max))
