import sys
from typing import Optional

DOCS_OFFICIAL_SITE = "https://abm4all.github.io/Melodie/html"
DOCS_MIRROR_SITE = "http://abm4all.gitee.io/melodie/html/"

HELP_URL_TEMPLATE = f"""
=====================Melodie Troubleshooting Tips==============================
The trouble shooting documentation for this error can be found at:

{DOCS_OFFICIAL_SITE}__URL__

or mirror site:

{DOCS_MIRROR_SITE}__URL__
================================================================================
"""


class OSTroubleShooter:
    """
    This class is a handler to print a link towards the help page.

    """
    _instance: Optional['OSTroubleShooter'] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OSTroubleShooter, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.cases = [(lambda s: "address already in use" in s or "Errno 10048" in s,
                       "/troubleshooting.html#port-already-in-use")]

    def handle_exc(self, exc: BaseException, exit_program=True, traceback=True):
        """
        Handle exception

        :param exc:
        :param exit_program: Program exit after printing troubleshooting url.
        :param traceback: Print traceback
        :return:
        """
        s = str(exc)
        for case in self.cases:
            if case[0](s):
                if traceback:
                    import traceback
                    traceback.print_exc()

                self._print_help_url(case[1])

                if exit_program:
                    sys.exit(1)

    @staticmethod
    def _print_help_url(url: str):
        print(HELP_URL_TEMPLATE.replace("__URL__", url), file=sys.stderr)
