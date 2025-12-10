# Virus Contagion Model (Basic)

This is a minimal example of an Agent-based Model (ABM) built with the Melodie framework. It demonstrates the core concepts of ABM without the complexity of spatial grids or social networks.

## Model Description

This model simulates the spread of a virus within a population where individuals interact randomly. It implements a classic **SIR (Susceptible-Infected-Recovered)** mechanism.

### Agents

Each agent represents a person with a specific health state:
- **Susceptible (0)**: Healthy and can be infected.
- **Infected (1)**: Currently carrying the virus and can infect others.
- **Recovered (2)**: Has recovered and is immune.

### Environment & Interaction

- **Environment**: A non-spatial "mean field". There is no grid or network topology.
- **Interaction**: In each time step (day), every agent randomly selects another agent from the population. If an infected agent contacts a susceptible agent, the virus may spread based on an `infection_probability`.

### Dynamics (Step Rules)

1. **Interaction Loop**: Agents interact and potentially transmit the virus.
2. **State Update**: Infected agents have a chance to recover based on a `recovery_probability`.
3. **Data Collection**: The system records the total number of Susceptible, Infected, and Recovered agents at the end of each step.

## Key Melodie Components Used

- `Model`: Manages the simulation loop.
- `Agent`: Defines individual behavior and state.
- `Scenario`: Manages parameters (e.g., infection rate, initial infected count).
- `DataCollector`: Tracks aggregate statistics for analysis.
