import time

from Melodie import run_profile, Agent
from Melodie.boost.agent_list import test_container, AgentList
from .config import model


def test_container_fcn():
    run_profile(test_container)
    # test_container()
