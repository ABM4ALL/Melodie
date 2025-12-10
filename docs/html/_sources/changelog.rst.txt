
Change Log
==========

Major Version 0.x
_________________

Version 1.1.0 (Dec. 10, 2025)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Add new examples and update documentation.
- Fixed small bugs in `Calibrator` and `Trainer`.
- Add a new parallel execution mode for the simulator: ``run_parallel_multithread`` based on Python 3.14+ free-threaded mode (No-GIL).
- Add thread-based parallel execution mode for `Calibrator` and `Trainer` via the ``parallel_mode`` parameter (recommended for Python 3.13+).
- Upgrade supported Python version from 3.12 to 3.14+ (tested on 3.14.2).

Version 1.0.0 (Mar. 14, 2024)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Clean up unused files and code.
- Simplify output format: CSV is now the default, with SQLite as an optional choice.
- Improve multi-processing performance for calibrator and trainer.
- Unify predefined names for special input files (e.g., ``SimulatorScenarios``, ``TrainerScenarios``, ``CalibratorScenarios``).
- Upgrade supported Python version from 3.8 to 3.12.

Version 0.8.0 (May. 10, 2023)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Remove Cythonized modules to improve maintainability and compatibility with PyPy.

Version 0.7.0 (Mar. 25, 2023)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Fix version compatibility issue for SQLAlchemy.
- Fix NumPy data type error (issues #12, #18).
- Remove unused dependencies from ``requirements.txt`` and ``setup.py``.
- Update documentation based on JOSS reviewer feedback.
- Fix path resolution issue on ``*nix`` platforms.
- Add a proxy router to support the gateway in MelodieStudio.

Version 0.6.0 (Jan. 04, 2023)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Modify ``Calibrator.distance`` method to use ``model`` instead of ``environment`` as a parameter.
- Modify parameter names in ``Trainer.add_agent_training_property``.
- Add the API Reference page to the documentation.

Version 0.5.0 (Dec. 17, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Add visualizer API for ``Grid`` and ``Network``.
- Fix port resource leak bugs in ``Trainer``.
- Fix a time-counting bug in the data collector.

Version 0.4.2 (Dec. 15, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Fix several bugs in the ``Calibrator`` class, related to logging, environment properties, multiple paths, and column names.

Version 0.4.1 (Dec. 12, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Complete and release the first version of the documentation.


Version 0.4.0 (Nov. 15, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Separate the ``MelodieInfra`` package, which contains infrastructure components.
- Add HTTP GET support to the WebSocket protocol.
- Add support for connection strings in the `DBConn` class.

Version 0.3.0 (Oct. 28, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Implement batch loading API for `DataframeInfo`.
- Implement Logger API.

Version 0.2.0 (Oct. 24, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Enable the DB module to read from specific directories.
- Add the ``filter`` method to select agents based on specified conditions.

Version 0.1.1 (Aug. 23, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Add a specific description for the assertion error in `Grid.set_spot_property`.

Version 0.1.0 (Jul. 22, 2022)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First version, with all main modules created.

Project Start (May. 10, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Start of the journey.
