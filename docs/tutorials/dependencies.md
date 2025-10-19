# Tutorial: Dependencies Management

`dmp-af` brings a new way to manage dependencies between models.
This is done by using the `dependencies` section in model's config.

There are two features that `dmp-af` brings to the table:

- skipping upstream dependencies
- wait not only last upstream model run, but all runs between the last and the current model runs

## Skipping upstream dependencies

Sometimes it's required to run the model as soon as possible, without waiting for the upstream models to be finished.
This can be achieved by setting `skip` to `true` in the `dependencies` section of the model's config.

```yaml
config:
  dependencies:
    upstream.model.name:
      skip: true
```

To try this feature, go
to `dmn_jaffle_analytics/ods/dmn_jaffle_analytics.ods.customers.sql` ([in the examples](https://github.com/dmp-labs/dmp-af/tree/main/examples/dags/jaffle_shop/dbt/models))
and add the following code to the `config` section:

```yaml
dependencies:
  dmn_jaffle_shop.stg.customers:
    skip: true
```

and run the [build_manifest.sh](https://github.com/dmp-labs/dmp-af/blob/main/examples/dags/build_manifest.sh) script to build the manifest file.

This will affect `dmn_jaffle_analytics__hourly` DAG: the `dmn_jaffle_analytics.ods.customers` model won't have
dependency on `dmn_jaffle_shop.stg.customers`.

|                With dependency                 |             Without dependency             |
|:----------------------------------------------:|:------------------------------------------:|
| ![](../static/not_skipped_dependency.png) | ![](../static/skipped_dependency.png) |


## Wait policy for upstream dependencies

If your model with rarer scheduling depends on the model with more frequent scheduling, you may want to wait for all
runs of the upstream model between the last and the current model runs. 

For example, if the model has `@daily` scheduling and depends on `@hourly` model, it's possible to wait for all 24 last 
runs (default behavior is to wait for only the last run).

This can be achieved by setting `wait_policy` to `all` in the `dependencies` section of the model's config:

```yaml
config:
  dependencies:
    upstream.model.name:
      wait_policy: all
```

!!! warning 
    This setting could generate a lot of tasks in your DAG. Be cautious here! If you still want to use this, consider updating number of slots in `dbt_sensor_pool` pool.


## List of Examples
1. [Basic Project](basic-project.md): a single domain, small tests, and a single target.
2. [Advanced Project](advanced-project.md): several domains, medium and large tests, and different targets.
4. [Manual scheduling](manual-scheduling.md): domains with manual scheduling.
5. [Maintenance and source freshness](maintenance.md): how to manage maintenance tasks and source freshness.
6. [Kubernetes tasks](kubernetes.md): how to run dbt models in Kubernetes.
7. [Integration with other tools](integrations.md): how to integrate dmp-af with other tools.
8. [\[Preview\] Extras and scripts](): available extras and scripts.