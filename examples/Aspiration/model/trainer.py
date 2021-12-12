
from Melodie import GeneticAlgorithmTrainer

class AspirationTrainer(GeneticAlgorithmTrainer):
    # 针对不同的scenario和training_scenario组合，每个组合都train一次。
    # 似乎scenario是更高一级的，在simulator和trainer之上注册的。
    pass




class Strategy:

    def __init__(self, conn, id_scenario):
        self.Conn = conn
        self.ID_Scenario = id_scenario
        self.ScenarioPara = DB().read_DataFrame(REG().Exo_ScenarioPara, self.Conn, ID_Scenario=self.ID_Scenario).iloc[0]
        self.StateCompanyNum = int(self.ScenarioPara["StateCompanyNum"])
        self.PrivateCompanyNum = int(self.ScenarioPara["PrivateCompanyNum"])
        self.StateControl = self.ScenarioPara["StateControl"]
        self.LearningPathNum = int(self.ScenarioPara["LearningPathNum"])
        self.StrategyPopulation = int(self.ScenarioPara["StrategyPopulation"])
        self.GeneLength = int(self.ScenarioPara["GeneLength"])
        self.MutationProb = self.ScenarioPara["MutationProb"]
        self.StrategyPara1_min = self.ScenarioPara["S1_min"]
        self.StrategyPara1_max = self.ScenarioPara["S1_max"]
        self.StrategyPara2_min = self.ScenarioPara["S2_min"]
        self.StrategyPara2_max = self.ScenarioPara["S2_max"]
        self.StrategyPara3_min = self.ScenarioPara["S3_min"]
        self.StrategyPara3_max = self.ScenarioPara["S3_max"]
        self.AgentStrategyColumn = ["ID_LearningPath", "ID_LearningGeneration", "AgentType", "ID_Agent", "ID_Strategy",
                                    "S11", "S12", "S13", "S14", "S15",
                                    "S21", "S22", "S23", "S24", "S25",
                                    "S31", "S32", "S33", "S34", "S35",
                                    "StrategyPara1", "StrategyPara2", "StrategyPara3",
                                    "Payoff", "Account", "AspirationSatisfyCount", "Technology",
                                    "ExplorationCount", "ExploitationCount", "LearnCount"]
        self.AgentStrategyDataType = {'ID_LearningPath': "INTEGER",
                                      'ID_LearningGeneration': "INTEGER",
                                      'AgentType': "TEXT",
                                      'ID_Agent': "INTEGER",
                                      'ID_Strategy': "INTEGER",
                                      'S11': "INTEGER",
                                      'S12': "INTEGER",
                                      'S13': "INTEGER",
                                      'S14': "INTEGER",
                                      'S15': "INTEGER",
                                      'S21': "INTEGER",
                                      'S22': "INTEGER",
                                      'S23': "INTEGER",
                                      'S24': "INTEGER",
                                      'S25': "INTEGER",
                                      'S31': "INTEGER",
                                      'S32': "INTEGER",
                                      'S33': "INTEGER",
                                      'S34': "INTEGER",
                                      'S35': "INTEGER",
                                      'StrategyPara1': "REAL",
                                      'StrategyPara2': "REAL",
                                      'StrategyPara3': "REAL",
                                      'Payoff': "REAL",
                                      'Account': "REAL",
                                      'AspirationSatisfyCount': "INTEGER",
                                      'Technology': "REAL",
                                      'ExplorationCount': "INTEGER",
                                      'ExploitationCount': "INTEGER",
                                      'LearnCount': "INTEGER"}
        self.StrategyPara1_BitStart = self.AgentStrategyColumn.index("S11")
        self.StrategyPara1_BitEnd = self.AgentStrategyColumn.index("S15")
        self.StrategyPara2_BitStart = self.AgentStrategyColumn.index("S21")
        self.StrategyPara2_BitEnd = self.AgentStrategyColumn.index("S25")
        self.StrategyPara3_BitStart = self.AgentStrategyColumn.index("S31")
        self.StrategyPara3_BitEnd = self.AgentStrategyColumn.index("S35")
        self.StrategyPara1Index = self.AgentStrategyColumn.index("StrategyPara1")
        self.StrategyPara2Index = self.AgentStrategyColumn.index("StrategyPara2")
        self.StrategyPara3Index = self.AgentStrategyColumn.index("StrategyPara3")
        self.PayoffIndex = self.AgentStrategyColumn.index("Payoff")
        self.AccountIndex = self.AgentStrategyColumn.index("Account")
        self.AspirationSatisfyCountIndex = self.AgentStrategyColumn.index("AspirationSatisfyCount")
        self.TechnologyIndex = self.AgentStrategyColumn.index("Technology")
        self.ExplorationCountIndex = self.AgentStrategyColumn.index("ExplorationCount")
        self.ExploitationCountIndex = self.AgentStrategyColumn.index("ExploitationCount")
        self.LearnCountIndex = self.AgentStrategyColumn.index("LearnCount")
        self.AgentStrategyProcess = pd.DataFrame(columns=self.AgentStrategyColumn)
        self.AgentStrategy = pd.DataFrame()

    def init_AgentStrategy(self, path, generation):
        AgentStrategyList = []
        for SC in range(0, self.StateCompanyNum):
            for strategy in range(0, self.StrategyPopulation):
                SC_list = [path + 1, generation + 1, "State", SC + 1, strategy + 1]
                for strategy_para in range(0, 3):
                    for bit in range(0, self.GeneLength):
                        SC_list.append(np.random.randint(0, 2))
                SC_list += [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                AgentStrategyList.append(SC_list)
        for PC in range(0, self.PrivateCompanyNum):
            for strategy in range(0, self.StrategyPopulation):
                PC_list = [path + 1, generation + 1, "Private", PC + 1, strategy + 1]
                for strategy_para in range(0, 3):
                    for bit in range(0, self.GeneLength):
                        PC_list.append(np.random.randint(0, 2))
                PC_list += [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                AgentStrategyList.append(PC_list)
        AgentStrategy = pd.DataFrame(AgentStrategyList, columns=self.AgentStrategyColumn)
        return AgentStrategy

    def record_AgentStrategyPayoff(self, strategy, agent_list):

        for agent in agent_list:
            RowIndex = self.AgentStrategy.index[(self.AgentStrategy["AgentType"] == agent.Type) &
                                                (self.AgentStrategy["ID_Agent"] == agent.ID) &
                                                (self.AgentStrategy["ID_Strategy"] == strategy + 1)][0]

            self.AgentStrategy.iloc[RowIndex, self.StrategyPara1Index] = agent.StrategyPara1
            self.AgentStrategy.iloc[RowIndex, self.StrategyPara2Index] = agent.StrategyPara2
            self.AgentStrategy.iloc[RowIndex, self.StrategyPara3Index] = agent.StrategyPara3
            self.AgentStrategy.iloc[RowIndex, self.AccountIndex] = agent.Account
            self.AgentStrategy.iloc[RowIndex, self.AspirationSatisfyCountIndex] = agent.AspirationSatisfyCount
            self.AgentStrategy.iloc[RowIndex, self.TechnologyIndex] = agent.Technology
            self.AgentStrategy.iloc[RowIndex, self.ExplorationCountIndex] = agent.ExplorationCount
            self.AgentStrategy.iloc[RowIndex, self.ExploitationCountIndex] = agent.ExploitationCount
            self.AgentStrategy.iloc[RowIndex, self.LearnCountIndex] = agent.LearnCount

            if agent.Type == "State":
                if self.StateControl == 1:
                    self.AgentStrategy.iloc[RowIndex, self.PayoffIndex] = agent.AspirationSatisfyCount
                elif self.StateControl == 0:
                    self.AgentStrategy.iloc[RowIndex, self.PayoffIndex] = agent.Account
                else:
                    pass
            elif agent.Type == "Private":
                self.AgentStrategy.iloc[RowIndex, self.PayoffIndex] = agent.Account
            else:
                pass
        return None

    def update_AgentStrategy(self, path, generation):
        AgentStrategyUpdate_list = []
        for SC in range(0, self.StateCompanyNum):
            SC_list = [path + 1, generation + 1, "State", SC + 1]
            AgentStrategyPool = self.AgentStrategy.loc[(self.AgentStrategy["AgentType"] == "State") &
                                                       (self.AgentStrategy["ID_Agent"] == SC + 1)]
            StrategyPara_matrix = AgentStrategyPool[self.AgentStrategyColumn[self.StrategyPara1_BitStart:self.StrategyPara3_BitEnd + 1]].values # ---> 有问题
            Payoff_array = AgentStrategyPool[self.AgentStrategyColumn[self.PayoffIndex]].values
            AgentStrategyPool_updateList = GA().GA_StrategyUpdate(StrategyPara_matrix, Payoff_array, self.MutationProb, self.StrategyPopulation).tolist()
            for strategy in range(0, self.StrategyPopulation):
                AgentStrategyUpdate_list.append(SC_list + [strategy + 1] + AgentStrategyPool_updateList[strategy] + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for PC in range(0, self.PrivateCompanyNum):
            PC_list = [path + 1, generation + 1, "Private", PC + 1]
            AgentStrategyPool = self.AgentStrategy.loc[(self.AgentStrategy["AgentType"] == "State") &
                                                       (self.AgentStrategy["ID_Agent"] == PC + 1)]
            StrategyPara_matrix = AgentStrategyPool[self.AgentStrategyColumn[self.StrategyPara1_BitStart:self.StrategyPara3_BitEnd + 1]].values
            Payoff_array = AgentStrategyPool[self.AgentStrategyColumn[self.PayoffIndex]].values
            AgentStrategyPool_updateList = GA().GA_StrategyUpdate(StrategyPara_matrix, Payoff_array, self.MutationProb, self.StrategyPopulation).tolist()
            for strategy in range(0, self.StrategyPopulation):
                AgentStrategyUpdate_list.append(PC_list + [strategy + 1] + AgentStrategyPool_updateList[strategy] + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        AgentStrategyUpdate = pd.DataFrame(AgentStrategyUpdate_list, columns=self.AgentStrategyColumn)
        return AgentStrategyUpdate

    def append_AgentStrategy(self):
        self.AgentStrategyProcess = self.AgentStrategyProcess.append(self.AgentStrategy, ignore_index=True)
        return None

    def gen_AgentStrategy(self, path, generation):
        if generation == 0:
            self.AgentStrategy = self.init_AgentStrategy(path, generation)
        else:
            self.AgentStrategy = self.update_AgentStrategy(path, generation)
        return None

    def translate_StrategyPara(self, binary_array, min_value, max_value):
        sum = 0
        real_maximum = 2 ** self.GeneLength - 1
        for bit in range(0, self.GeneLength):
            sum += binary_array[bit] * 2 ** (self.GeneLength - 1 - bit)
        real_value = min_value + sum/real_maximum * (max_value - min_value)
        return real_value

    def calibrate_AgentStrategyPara(self, strategy, agent_list):
        for agent in agent_list:
            AgentStrategyRow = self.AgentStrategy.loc[(self.AgentStrategy["AgentType"] == agent.Type) &
                                                      (self.AgentStrategy["ID_Agent"] == agent.ID) &
                                                      (self.AgentStrategy["ID_Strategy"] == strategy + 1)].iloc[0]
            agent.StrategyPara1 = self.translate_StrategyPara(AgentStrategyRow[self.AgentStrategyColumn[self.StrategyPara1_BitStart:self.StrategyPara1_BitEnd + 1]].values,
                                                              self.StrategyPara1_min,
                                                              self.StrategyPara1_max)
            agent.StrategyPara2 = self.translate_StrategyPara(AgentStrategyRow[self.AgentStrategyColumn[self.StrategyPara2_BitStart:self.StrategyPara2_BitEnd + 1]].values,
                                                              self.StrategyPara2_min,
                                                              self.StrategyPara2_max)
            agent.StrategyPara3 = self.translate_StrategyPara(AgentStrategyRow[self.AgentStrategyColumn[self.StrategyPara3_BitStart:self.StrategyPara3_BitEnd + 1]].values,
                                                              self.StrategyPara3_min,
                                                              self.StrategyPara3_max)
        return None

    def save_AgentStrategyProcess(self):
        self.AgentStrategyProcess.to_sql(REG().Res_AgentLearning + "_S" + str(self.ID_Scenario), self.Conn,
                                         index=False, if_exists='replace', chunksize=1000, dtype=self.AgentStrategyDataType)
        return None

    def calibrate_AgentSimulationStrategyPara(self, agent_list):
        # probabilistically select the real strategy parameter values and assign them to the agents
        return None

