# covid_contagion_calibrator

This example extends the base COVID contagion model with `Calibrator`. It uses a genetic algorithm to search parameters such as `infection_prob` so that the model output approaches a target value.

On Python 3.13+ this example uses thread-based parallelism by default, which avoids the local TCP socket requirement of the process-based `rpyc` worker mode.

Run from the repository root:

```bash
python -m examples.covid_contagion_calibrator.main
```

Outputs are written to `examples/covid_contagion_calibrator/data/output/`.
