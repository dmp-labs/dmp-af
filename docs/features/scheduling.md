# Scheduling

Flexible scheduling for different data refresh requirements.

## Multiple Schedules

Run different models on different schedules within the same project:

- `@every15minutes`: Real-time data
- `@hourly`: Frequent updates
- `@daily`: Standard batch processing
- `@weekly/@monthly`: Reports and aggregations
- `@manual`: On-demand execution

## Schedule Shifts

Offset schedules to coordinate dependencies or distribute load.

## Learn More

- [Schedules Configuration](../configuration/schedules.md)
- [Manual Scheduling Tutorial](../tutorials/manual-scheduling.md)
