# README

This Project ***ABM_Framework*** is a general framework that can be used to develop agent-based models for specific uses. For illustration, a minimized example is provided. 

This example is about the wealth distribution in the society, exploring how "Gini index" can be influenced by the productivity and equality of people. After initialization, each agents get some money in their account. Then, in each period, all the agents go through following two processes:

- MoneyProduce: randomly receive some money.
- MoneyTransfer: in each period, there are multiple rounds. In each round, two agents are randomly selected and they play a game. The winner will take 1 dollar from the loser.

The system calculates the "total wealth" and "gini index" in each period.

There are two key parameters to discuss in the example:

- Productivity: the probability of agents to successfully produce some money at the beginning of each period.
- Winning probability of richer player: in each game between two randomly selected players, the result is probabilistically decided by a pre-defined parameter, i.e. the probability that the richer player will win the game. With this parameter, we introduce "allocation equality" in the model

By changing these two parameters, we can explore the following question: how is the "Gini index" influenced by the productivity and equality in the society.

