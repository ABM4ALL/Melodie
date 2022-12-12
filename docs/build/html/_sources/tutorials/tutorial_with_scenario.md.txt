# Scenario And Batch Experiment

## Scenario
In the former example [Basic Tutorial](./basic_tutorial.html) we introduced a simple model of gini index, and this model really revealed something. However, consider this issue:

What is the relationship between gini index and production in each step (`productivity`)? Assume that the probability that richer agent wins (`rich_win_prob`) is 0.8. 

To find how production rate affect the gap of between the rich and poor, we should run a multi-run simulation with different parameters like this:

|id|productivity|rich_win_prob|
|---|---|---|
|0|0.1|0.8|
|1|0.5|0.8|
|2|1|0.8|
|3|1.5|0.8|
|4|2|0.8|

Each row in the table above can be  `Scenario` in Melodie.

The code of `Agent` should be modified like this:
```python
class GiniAgent(Agent):

    def setup(self):
        self.account = .0
        self.productivity = 0.1  # value could be: [0.1, 0.5, 1.0, 1.5, 2.0]

    def go_produce(self):
        self.account += self.productivity
```


### 