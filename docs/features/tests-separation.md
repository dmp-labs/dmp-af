# Test Separation

Separate small, medium, and large tests into different execution paths.

## Overview

dmp-af can separate dbt tests by size for optimized execution.

## Test Categories

- **Small**: Fast unit tests
- **Medium**: Integration tests
- **Large**: Full data quality checks

## Benefits

- Run small tests more frequently
- Save resources by running large tests less often
- Fail fast with quick tests
- Comprehensive validation with slow tests

## Learn More

See [Advanced Project Tutorial](../tutorials/advanced-project.md) for test configuration.
