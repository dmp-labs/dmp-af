# Docker Compose Setup

This guide shows you how to run dmp-af with Apache Airflow using Docker Compose.

## Why Docker Compose?

Docker Compose provides:

- **Quick Setup**: Get Airflow running in minutes
- **Isolated Environment**: No conflicts with local installations
- **Production-Like**: Similar to production deployment
- **Easy Cleanup**: Remove everything with one command

## Prerequisites

Install Docker and Docker Compose:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Compose)
- Or Docker Engine + Docker Compose plugin

Verify installation:

```bash
docker --version
docker compose version
```

## Setup Steps

### 1. Navigate to Examples Directory

```bash
cd examples
```

### 2. Set Up Environment

Initialize environment variables:

```bash
source .env
```

The `.env` file contains:

```bash
AIRFLOW_UID=50000
AIRFLOW_GID=0
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

### 3. Build dbt Manifest

Before starting Airflow, compile the dbt project:

```bash
cd dags
./build_manifest.sh
cd ..
```

This creates the `target/manifest.json` that dmp-af needs.

### 4. Start Services

Launch all Docker containers:

```bash
docker compose up --force-recreate -d --build
```

This command:

- `--force-recreate`: Recreates containers even if config unchanged
- `-d`: Runs in detached mode (background)
- `--build`: Rebuilds images if Dockerfile changed

### 5. Wait for Initialization

Services need a few minutes to initialize. Check status:

```bash
docker compose ps
```

Wait until all services show "healthy" or "running".

### 6. Access Airflow UI

Open your browser to:

```
http://localhost:8080
```

**Login credentials:**

- Username: `airflow`
- Password: `airflow`

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

## Working with Docker Compose

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs webserver
docker compose logs scheduler

# Follow logs (real-time)
docker compose logs -f scheduler
```

### Execute Commands Inside Containers

```bash
# Access Airflow CLI
docker compose exec webserver airflow version

# Create Airflow pool
docker compose exec webserver airflow pools set dbt_dev 4 "Dev pool"

# Access Python shell
docker compose exec webserver python
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart scheduler
```

### Stop Services

```bash
# Stop without removing containers
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove everything including volumes
docker compose down --volumes --remove-orphans
```

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
docker compose up --build -d
```

If you modify DAG files:

- Changes are reflected automatically (mounted volume)
- Wait for scheduler to pick up changes (~30 seconds)

## Troubleshooting

### Services Won't Start

Check logs for errors:

```bash
docker compose logs webserver
docker compose logs scheduler
```

Common issues:

- Port 8080 already in use: Change port in `docker-compose.yaml`
- Insufficient memory: Allocate more RAM to Docker
- Permission issues: Check `AIRFLOW_UID` in `.env`

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
docker compose down --volumes --remove-orphans
```

This removes:

- All containers
- All volumes (including database)
- All networks

### Keep Data, Remove Containers

```bash
docker compose down
```

This keeps:

- Volume data (database, logs)

Restart with:

```bash
docker compose up -d
```

## Production Considerations

The provided Docker Compose setup is for **development only**. For production:

- Use production-grade database (not Docker Postgres)
- Configure proper authentication
- Set up SSL/TLS
- Use KubernetesExecutor instead of CeleryExecutor
- Implement proper monitoring and logging
- Follow [Airflow's production deployment guide](https://airflow.apache.org/docs/apache-airflow/stable/production-deployment.html)

## Next Steps

With Docker Compose running:

- **[Quick Start](quick-start.md)** - Run your first DAG
- **[Tutorials](../tutorials/index.md)** - Explore examples
- **[Configuration](../configuration/index.md)** - Customize your setup
