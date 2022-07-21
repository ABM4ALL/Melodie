import copy

from Melodie.basic import MelodieExceptions


class CalibratorAlgorithmMeta:
    """
    Record the current scenario, params scenario, path and generation
    of trainer.

    """

    def __init__(self):
        self._freeze = False
        self.calibrator_scenario_id = 0
        self.calibrator_params_id = 1
        self.path_id = 0
        self.iteration = 0

    def to_dict(self, public_only=False):

        if public_only:
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return copy.copy(self.__dict__)

    def __repr__(self):
        return f"<{self.to_dict()}>"

    def __setattr__(self, key, value):
        if (not hasattr(self, "_freeze")) or (not self._freeze):
            super().__setattr__(key, value)
        else:
            if key in self.__dict__:
                super().__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class TrainerAlgorithmMeta:
    """
    Record the current scenario, params scenario, path and generation
    of trainer.

    """

    def __init__(self):
        self._freeze = False
        self.trainer_scenario_id = 0
        self.trainer_params_id = 1
        self.path_id = 0
        self.iteration = 0

    def to_dict(self, public_only=False):

        if public_only:
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return copy.copy(self.__dict__)

    def __repr__(self):
        return f"<{self.to_dict()}>"

    def __setattr__(self, key, value):
        if (not hasattr(self, "_freeze")) or (not self._freeze):
            super().__setattr__(key, value)
        else:
            if key in self.__dict__:
                super(TrainerAlgorithmMeta, self).__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class GATrainerAlgorithmMeta(TrainerAlgorithmMeta):
    def __init__(self):
        super().__init__()
        self.chromosome_id = 0
        self._freeze = True


class GACalibratorAlgorithmMeta(CalibratorAlgorithmMeta):
    def __init__(self):
        super(GACalibratorAlgorithmMeta, self).__init__()
        self.chromosome_id = 0
        self._freeze = True
