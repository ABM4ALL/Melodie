# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
from typing import ClassVar

import numpy as np
import pandas.io.sql

from ..Config import REG, GiniScenario
from Melodie.DB import DB
from Melodie.Agent import Agent

logger = logging.getLogger(__name__)


class TableGenerator:

    def __init__(self, conn, scenario: "GiniScenario", agentClass: ClassVar[Agent]):
        """
        Pass the class of agent, to get the data type that how the properties are saved into database.
        :param conn:
        :param scenario:
        :param agentClass:
        """
        self.Conn = conn
        self.Scenario = scenario
        self.agentClass = agentClass

        try:
            DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.Scenario.ID_Scenario).iloc[0]
        except pandas.io.sql.DatabaseError:
            logger.warning(
                f"Table {REG().Exo_ScenarioPara} does not exist and it will be created storing default value")
            DB().createScenario(REG().Exo_ScenarioPara, self.Conn, self.Scenario, dtype=self.Scenario.types)

    def gen_AgentParaTable(self):
        agentNum = self.Scenario.AgentNum
        intialAccountMin = self.Scenario.AgentAccount_min
        intialAccountMax = self.Scenario.AgentAccount_max
        agentProductivity = self.Scenario.AgentProductivity

        agentParaTable = np.zeros((agentNum, 3))
        for agent in range(0, agentNum):
            agentParaTable[agent][0] = agent + 1
            agentParaTable[agent][1] = np.random.randint(intialAccountMin, intialAccountMax + 1)
            agentParaTable[agent][2] = agentProductivity

        data_column = self.agentClass.types
        DB().write_DataFrame(agentParaTable, REG().Gen_AgentPara + "_S" + str(self.Scenario.ID_Scenario),
                             data_column.keys(), self.Conn, dtype=data_column)

        return None

    def run(self):
        self.gen_AgentParaTable()
