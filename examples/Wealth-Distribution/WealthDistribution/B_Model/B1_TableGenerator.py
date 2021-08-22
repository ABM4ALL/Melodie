# -*- coding: utf-8 -*-
__author__ = 'Songmin'

import logging
from typing import ClassVar

import numpy as np
import pandas.io.sql

from ..Config import REG
from Melodie.DB import DB
from Melodie.Agent import Agent
logger = logging.getLogger(__name__)


class TableGenerator:

    def __init__(self, conn, id_scenario, agentClass: ClassVar[Agent]):
        """
        Pass the class of agent, to get the data type that how the properties are saved into database.
        :param conn:
        :param id_scenario:
        :param agentClass:
        """
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.agentClass = agentClass

        try:
            self.ScenarioPara = \
                DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]
        except pandas.io.sql.DatabaseError:
            logger.warning(
                f"Table {REG().Exo_ScenarioPara} does not exist and it will be created storing default value")

            self.ScenarioPara = {"ID_Scenario": 1.0,
                                 "Periods": 200.0,
                                 "AgentNum": 100.0,
                                 "AgentAccount_min": 0.0,
                                 "AgentAccount_max": 100.0,
                                 "AgentProductivity": 0.5,
                                 "TradeNum": 100.0,
                                 "RichWinProb": 0.2}
            types = {"ID_Scenario": 'FLOAT',
                     "Periods": 'INT',
                     "AgentNum": 'INT',
                     "AgentAccount_min": 'REAL',
                     "AgentAccount_max": 'REAL',
                     "AgentProductivity": 'REAL',
                     "TradeNum": "REAL",
                     "RichWinProb": 'REAL'}
            DB().createSettings(REG().Exo_ScenarioPara, self.Conn, self.ScenarioPara, dtype=types)

    def gen_AgentParaTable(self):
        AgentNum = int(self.ScenarioPara["AgentNum"])
        IntialAccountMin = self.ScenarioPara["AgentAccount_min"]
        IntialAccountMax = self.ScenarioPara["AgentAccount_max"]
        AgentProductivity = self.ScenarioPara["AgentProductivity"]

        AgentParaTable = np.zeros((AgentNum, 3))
        for agent in range(0, AgentNum):
            AgentParaTable[agent][0] = int(agent + 1)
            AgentParaTable[agent][1] = np.random.randint(IntialAccountMin, IntialAccountMax + 1)
            AgentParaTable[agent][2] = AgentProductivity

        data_column = self.agentClass.types
        DB().write_DataFrame(AgentParaTable, REG().Gen_AgentPara + "_S" + str(self.ID_Scenario),
                             data_column.keys(), self.Conn, dtype=data_column)

        return None

    def run(self):
        self.gen_AgentParaTable()
