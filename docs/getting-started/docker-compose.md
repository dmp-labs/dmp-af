# Docker Compose Setup

This guide shows you how to run dmp-af with Apache Airflow using Docker Compose.

## Why Docker Compose?

Docker Compose provides:

- **Quick Setup**: Get Airflow running in minutes
- **Isolated Environment**: No conflicts with local installations
- **Production-Like**: Similar to production deployment
- **Easy Cleanup**: Remove everything with one command
- **Multi-Version Support**: Test with both Airflow 2.x and 3.x

## Prerequisites

Install Docker and Docker Compose:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Compose)
- Or Docker Engine + Docker Compose plugin

Verify installation:

```bash
docker --version
docker compose version
```

## Quick Start with Management Script

We provide a convenient `manage-airflow.sh` script that handles all setup automatically.

### 1. Navigate to Examples Directory

```bash
cd examples
```

### 2. Start Airflow

Choose your Airflow version:

**For Airflow 2.x:**

```bash
./manage-airflow.sh up 2
```

**For Airflow 3.x:**

```bash
./manage-airflow.sh up 3
```

The script automatically:

- Creates `.env` file with OS-specific settings
- Builds the dbt manifest
- Starts all Docker containers
- Creates required Airflow pools

### 3. Wait for Initialization

Services need a few minutes to initialize. Check status:

```bash
# For Airflow 2.x
./manage-airflow.sh status 2

# For Airflow 3.x
./manage-airflow.sh status 3
```

Wait until all services show "healthy" or "running".

### 4. Access Airflow UI

Open your browser to:

```
http://localhost:8080
```

**Login credentials:**

- Username: `airflow`
- Password: `airflow`

!!! note "Airflow 3 Differences"
Airflow 3.x uses an API server instead of a traditional webserver, but the UI experience is similar.

## Included Services

The Docker Compose setup includes:

### Core Services

- **webserver**: Airflow UI (port 8080)
- **scheduler**: DAG scheduling and execution
- **worker**: Task execution (CeleryExecutor)
- **triggerer**: For deferrable operators

### Supporting Services

- **postgres**: Airflow metadata database
- **redis**: Celery message broker
- **flower**: Celery monitoring (port 5555)

### Volumes

Data persists in Docker volumes:

- `postgres-db-volume`: Database data
- `./dags`: DAG files (mounted from host)
- `./logs`: Airflow logs (mounted from host)
- `./plugins`: Custom plugins (mounted from host)

## Management Script Reference

### Common Operations

**Start services:**

```bash
./manage-airflow.sh up [2|3]
```

**Stop services:**

```bash
./manage-airflow.sh down [2|3]
```

**Stop and remove volumes:**

```bash
./manage-airflow.sh down [2|3] -v
```

**Restart services:**

```bash
./manage-airflow.sh restart [2|3]
```

**Rebuild images:**

```bash
./manage-airflow.sh build [2|3] --no-cache
```

**View logs:**

```bash
# All services
./manage-airflow.sh logs [2|3]

# Last 100 lines
./manage-airflow.sh logs [2|3] --tail=100

# Follow logs (real-time)
./manage-airflow.sh logs [2|3] -f
```

**Check service status:**

```bash
./manage-airflow.sh status [2|3]
```

**List running containers:**

```bash
./manage-airflow.sh ps [2|3]
```

### Advanced Usage

**Pass additional Docker Compose arguments:**

```bash
# Force recreate containers
./manage-airflow.sh up 2 --force-recreate

# Restart specific service
./manage-airflow.sh restart 2 airflow-webserver

# View logs for specific service
./manage-airflow.sh logs 3 airflow-scheduler --tail=50
```

### Switching Between Airflow Versions

!!! warning "Port Conflicts"
Both Airflow 2.x and 3.x use port 8080. Stop one version before starting another:

    ```bash
    # Stop Airflow 2.x
    ./manage-airflow.sh down 2

    # Start Airflow 3.x
    ./manage-airflow.sh up 3
    ```

### Execute Commands Inside Containers

For direct access to containers, you can still use `docker compose`:

```bash
# Access Airflow CLI (Airflow 2.x)
docker compose exec webserver airflow version

# Access Airflow CLI (Airflow 3.x)
docker compose -f docker-compose3.yaml exec api-server airflow version

# Access Python shell
docker compose exec webserver python

# Create Airflow pool manually
docker compose exec webserver airflow pools set dbt_dev 4 "Dev pool"
```

!!! note "Automatic Pool Creation"
The `manage-airflow.sh` script automatically creates required pools (`dbt_dev`, `dbt_sensor_pool`), so manual pool
creation is usually unnecessary.

## Configuration

### Customizing the Setup

Edit `docker-compose.yaml` to:

- Change ports
- Add environment variables
- Mount additional volumes
- Adjust resource limits

Example - Change webserver port:

```yaml
webserver:
  ports:
    - "9090:8080"  # Changed from 8080:8080
```

### Environment Variables

Add to `.env` file:

```bash
# Airflow configuration
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True

# dmp-af specific
DBT_TARGET=dev
DBT_PROJECT_DIR=/opt/airflow/dags/jaffle_shop
```

## Using dmp-af with Docker

### Add DAG Files

DAG files in `examples/dags/` are automatically mounted to `/opt/airflow/dags/` in containers.

Create a new DAG:

```python
# examples/dags/my_dag.py
from dmp_af.dags import compile_dmp_af_dags
from dmp_af.conf import Config, DbtProjectConfig

config = Config(
    dbt_project=DbtProjectConfig(
        dbt_project_name='my_project',
        dbt_project_path='/opt/airflow/dags/my_project',
        # ... other config
    )
)

dags = compile_dmp_af_dags(
    manifest_path='/opt/airflow/dags/my_project/target/manifest.json',
    config=config,
)

for dag_name, dag in dags.items():
    globals()[dag_name] = dag
```

!!! note "Container Paths"
Use container paths (e.g., `/opt/airflow/dags/...`) in DAG configuration, not host paths.

### Rebuild After Changes

If you modify `Dockerfile` or requirements:

```bash
# For Airflow 2.x
./manage-airflow.sh build 2
./manage-airflow.sh up 2

# For Airflow 3.x
./manage-airflow.sh build 3
./manage-airflow.sh up 3
```

If you modify DAG files:

- Changes are reflected automatically (mounted volume)
- Wait for scheduler to pick up changes (~30 seconds)

## Troubleshooting

### Services Won't Start

Check logs for errors:

```bash
# For Airflow 2.x
./manage-airflow.sh logs 2 webserver
./manage-airflow.sh logs 2 scheduler

# For Airflow 3.x
./manage-airflow.sh logs 3 api-server
./manage-airflow.sh logs 3 scheduler
```

Common issues:

- Port 8080 already in use: Stop other Airflow instance with `./manage-airflow.sh down [2|3]`
- Insufficient memory: Allocate more RAM to Docker
- Permission issues: The `manage-airflow.sh` script automatically sets correct `AIRFLOW_UID`

### DAGs Not Appearing

1. Verify DAG file has no syntax errors:

```bash
docker compose exec webserver python /opt/airflow/dags/your_dag.py
```

2. Check DAG import errors:

```bash
docker compose exec webserver airflow dags list-import-errors
```

3. Ensure manifest exists:

```bash
docker compose exec webserver ls -l /opt/airflow/dags/jaffle_shop/target/manifest.json
```

### Slow Performance

Adjust resource allocation in Docker Desktop:

- **CPUs**: 4+
- **Memory**: 8 GB+
- **Swap**: 2 GB+

### Database Connection Issues

Reset the database:

```bash
docker compose down --volumes
docker compose up -d
```

## Cleanup

### Remove Everything

```bash
# For Airflow 2.x
./manage-airflow.sh down 2 --volumes --remove-orphans

# For Airflow 3.x
./manage-airflow.sh down 3 --volumes --remove-orphans
```

This removes:

- All containers
- All volumes (including database)
- All networks

### Keep Data, Remove Containers

```bash
# For Airflow 2.x
./manage-airflow.sh down 2

# For Airflow 3.x
./manage-airflow.sh down 3
```

This keeps:

- Volume data (database, logs)

Restart with:

```bash
./manage-airflow.sh up [2|3]
```

## Production Considerations

The provided Docker Compose setup is for **development only**. For production:

- Use production-grade database (not Docker Postgres)
- Configure proper authentication
- Set up SSL/TLS
- Use KubernetesExecutor instead of CeleryExecutor
- Implement proper monitoring and logging
-
Follow [Airflow's production deployment guide](https://airflow.apache.org/docs/apache-airflow/stable/production-deployment.html)

## Next Steps

With Docker Compose running:

- **[Quick Start](quick-start.md)** - Run your first DAG
- **[Tutorials](../tutorials/index.md)** - Explore examples
- **[Configuration](../configuration/index.md)** - Customize your setup
