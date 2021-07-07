# README

This project is supposed to be developed as a general framework that can be used to establish agent-based models for specific uses. Current main contributors are **Songmin YU** and **Zhanyi HOU**. 



#### 1 Meetings

- 20210707 - Brief exchange of development ideas
- 2021080x - to be settled



#### 2 Current Step

##### Songmin

- plan the modules that will be covered in the framework

##### Zhanyi

- go through the code of MESA and see what we could learn from and build based on them



#### 3 Ideas













---

#### Application Example

For illustration, a minimized example on **Wealth Distribution** is provided as below. 

This example explores how "Gini index" can be influenced by the productivity and equality of people. After initialization, each agents get some money in their account. Then, in each period, all the agents go through following two processes:

- MoneyProduce: randomly receive some money.
- MoneyTransfer: in each period, there are multiple rounds. In each round, two agents are randomly selected and they play a game. The winner will take 1 dollar from the loser.

The system calculates the "total wealth" and "gini index" in each period.

There are two key parameters to discuss in the example:

- Productivity: the probability of agents to successfully produce some money at the beginning of each period.
- Winning probability of richer player: in each game between two randomly selected players, the result is probabilistically decided by a pre-defined parameter, i.e. the probability that the richer player will win the game. With this parameter, we introduce "allocation equality" in the model

By changing these two parameters, we can explore the following question: how is the "Gini index" influenced by the productivity and equality in the society.

