"""
Main entry point for running the Mesa-based COVID-19 contagion model.

This script reads scenario parameters from a CSV file, runs the simulation
for each scenario and each run number, and saves the collected agent and model
data to separate CSV files in the output directory.

Dependencies:
    - mesa>=3.0 (Note: Mesa 3.0+ changes how agents are stored and accessed)
    - pandas
    - numpy
"""
import os
import pandas as pd

from core.model import CovidModel


def run_scenarios() -> None:
    """
    Loads scenarios, runs the model for each, and saves the results.
    """
    # Define file paths relative to this script.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "data", "input", "SimulatorScenarios.csv")
    output_dir = os.path.join(base_dir, "data", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Read scenarios from the CSV file.
    scenarios = pd.read_csv(input_path).to_dict(orient="records")

    agents_outputs = []
    model_outputs = []

    # Iterate through each scenario defined in the CSV.
    for scenario in scenarios:
        scenario_id = int(scenario.get("id", 0))
        run_num = int(scenario.get("run_num", 1))

        # Run the model multiple times for each scenario (for stochasticity).
        for run_id in range(run_num):
            print(f"Running Mesa model: Scenario {scenario_id}, Run {run_id}...")
            # Initialize and run the model with parameters from the current scenario.
            model = CovidModel(**scenario)
            model.run_model()

            # Collect and format data for this run.
            agents_df = model.datacollector.get_agent_vars_dataframe()
            model_df = model.datacollector.get_model_vars_dataframe()
            agents_outputs.append(
                CovidModel.format_agent_df(agents_df, scenario_id, run_id)
            )
            model_outputs.append(
                CovidModel.format_model_df(model_df, scenario_id, run_id)
            )

    # Concatenate and save all collected data.
    if agents_outputs:
        agents_all = pd.concat(agents_outputs, ignore_index=True)
        agents_all.to_csv(
            os.path.join(output_dir, "Result_Mesa_Agents.csv"), index=False
        )
    if model_outputs:
        env_all = pd.concat(model_outputs, ignore_index=True)
        env_all.to_csv(
            os.path.join(output_dir, "Result_Mesa_Environment.csv"), index=False
        )
    print("Mesa simulation runs complete.")


if __name__ == "__main__":
    run_scenarios()
