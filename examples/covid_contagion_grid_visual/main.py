"""
Main entry point for the visual grid-based CovidContagion example.

Usage: python main.py
Then open http://localhost:8089 in browser.
"""
import os
from Melodie import Config
from MelodieStudio.main import studio_main

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    config = Config(
        project_name="CovidContagionGridVisual",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
        visualizer_entry=os.path.join(base_dir, "run_visualizer.py"),
        visualizer_port=8765,
    )

    studio_main(config)
