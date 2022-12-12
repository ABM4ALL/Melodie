
Change Log
=========

Roadmap
_______

- Add file `.gexf` format for network.
- Optimize and re-arrange the visualizer API.
- Modify id_run and id_scenario inside the data collector.
- Change the name of the base class of Simulator to `ModelRunningManager`.
- Change name: DataCollector.status -> `DataCollector.running_manager_mode`.
- Visualizer port should be dynamically allocated. The only port needed to be configured is the port of MelodieStudio. 
- Multiple graph types support!

Major Version 0.x
_________________

v0.4.0 (Nov. 15, 2022)
~~~~~~

- Separated the MelodieInfra package containing infrastructure.
- Added HTTP Get support in the websocket protocol.
- Support for connection string in `DBConn` class.

v0.3.0 (Oct. 28, 2022)
~~~~~~

- Batch load API for `DataframeInfo`.
- Logger API.

v0.2.0 (Oct. 24, 2022)
~~~~~~

- DB module supported reading from specific directories.
- Added `filter` method to select agents of given conditions.

v0.1.1 (Aug. 23, 2022)
~~~~~~

- Added specific description for assertion error in `Grid.set_spot_property`.

v0.1.0 (Jul. 22, 2022)
~~~~~~

- first version, all main modules created.

Start (May. 10, 2021)
~~~~~~

- Start of the journey.
