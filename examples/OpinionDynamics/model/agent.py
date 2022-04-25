import logging

from typing import TYPE_CHECKING

from Melodie import Agent

if TYPE_CHECKING:
    from .scenario import OpinionDynamicsScenario
logger = logging.getLogger(__name__)


class OpinionDynamicsAgent(Agent):
    scenario: 'OpinionDynamicsScenario'

    def setup(self):
        self.opinion_level = 0.0
        self.opinion_radius = 0.0

    def reset_communication_track(self):
        self.communication_action = "no"
        self.communication_neighbor_id = -1
        self.communication_result = "-"

    def update_opinion_level_with_neighbor(self, neighbor: 'OpinionDynamicsAgent'):
        """
        The communication process between two agents is modeled following the "relative agreement algorithm".
        Reference:
        Deffuant, G., Amblard, F., Weisbuch, G., & Faure, T. (2002).
        How can extremism prevail? A study based on the relative agreement interaction model.
        Journal of artificial societies and social simulation, 5(4).

        :param neighbor:
        :return:
        """
        self.communication_action = "yes"
        self.communication_neighbor_id = neighbor.id
        neighbor_opinion_level = neighbor.opinion_level
        neighbor_opinion_radius = neighbor.opinion_radius

        overlap = min(neighbor_opinion_level + neighbor_opinion_radius,
                      self.opinion_level + self.opinion_radius) - \
                  max(neighbor_opinion_level - neighbor_opinion_radius,
                      self.opinion_level - self.opinion_radius)
        non_overlap = 2 * neighbor_opinion_radius - overlap
        agreement = overlap - non_overlap
        relative_agreement = agreement / (2 * neighbor_opinion_radius)
        if relative_agreement <= 0:
            self.communication_result = "unchanged"
            pass
        else:
            self.communication_result = "changed"
            self.opinion_level = self.opinion_level + \
                                 self.scenario.relative_agreement_param * relative_agreement * \
                                 (neighbor_opinion_level - self.opinion_level)
            self.opinion_radius = self.opinion_radius + \
                                  self.scenario.relative_agreement_param * relative_agreement * \
                                  (neighbor_opinion_radius - self.opinion_radius)
