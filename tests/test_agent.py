import pytest
from Melodie.Agent import Agent

def test_fib_10():
	assert(Agent().fibonacci(10) == 55)

def test_fib_not_20():
	assert(Agent().fibonacci(20) != 20)