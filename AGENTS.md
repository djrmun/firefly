This is an automated agent.

## Project: firefly

The goal of this project is to create a Python-based tool to monitor network performance to a set of URLs.

### Plan

The plan is laid out in the `set_plan` tool. I will follow it step-by-step.

### Coding Conventions

*   Language: Python 3
*   Style: PEP 8
*   Modules:
    *   `pycurl` for HTTP requests and detailed metrics.
    *   `PyYAML` for configuration.
    *   `schedule` for scheduling.
    *   `pandas` for analysis.
    *   `matplotlib` for plotting.
    *   `sqlite3` for storage.
*   All new code should be placed in the `firefly/` directory.

### Testing

Before submitting, I will ensure that the tool runs and that I have tested its functionality. This includes:
1.  Running the monitoring.
2.  Checking that data is stored in the database.
3.  Running the analysis and generating a report/plot.
