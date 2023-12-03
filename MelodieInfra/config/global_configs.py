class MelodieGlobalConfig:
    class Logger:
        TIME_ROUND_DIGITS = 3

        @staticmethod
        def round_elapsed_time(t: float):
            return round(t, MelodieGlobalConfig.Logger.TIME_ROUND_DIGITS)
