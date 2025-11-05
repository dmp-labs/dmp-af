"""Helper utilities for Airflow 3+ DAG serialization in tests.

In Airflow 3+, when using methods like dag.create_dagrun(), DAGs must be
serialized in the database first. However, the dag.test() method works
without serialization as it runs in a single Python process.

This module provides utilities to serialize DAGs for testing purposes.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airflow import DAG


def serialize_dag_for_test(dag: 'DAG') -> None:
    """Serialize a DAG to the Airflow database for testing.

    This is required in Airflow 3+ when using dag.create_dagrun() or other
    database-dependent methods. The dag.test() method doesn't require this.

    Args:
        dag: The DAG object to serialize

    Note:
        This function uses Airflow's internal serialization API. It should
        only be used in testing contexts.
    """
    try:
        # Airflow 3+ uses a new serialization approach
        from airflow.models import DagModel
        from airflow.models.dagbundle import DagBundleModel
        from airflow.serialization.serialized_objects import LazyDeserializedDAG
        from airflow.utils import timezone
        from airflow.utils.session import create_session

        bundle_name = 'test-bundle'

        # Store in the database
        with create_session() as session:
            # Create bundle entry if it doesn't exist (required for foreign key)
            bundle = session.query(DagBundleModel).filter(DagBundleModel.name == bundle_name).first()
            if not bundle:
                bundle = DagBundleModel(name=bundle_name)
                session.add(bundle)
                session.flush()  # Ensure bundle is created before DAG

            # Create or update DagModel entry
            dag_model = session.query(DagModel).filter(DagModel.dag_id == dag.dag_id).first()
            if not dag_model:
                dag_model = DagModel(dag_id=dag.dag_id)
                session.add(dag_model)

            dag_model.fileloc = dag.fileloc or 'test_dag'
            dag_model.is_active = True
            dag_model.last_parsed_time = timezone.utcnow()
            dag_model.is_paused = False
            dag_model.bundle_name = bundle_name

            # Create a LazyDeserializedDAG which is what write_dag expects
            # LazyDeserializedDAG only needs the 'data' field
            lazy_dag = LazyDeserializedDAG.from_dag(dag)

            # Now store it in the database
            from airflow.models.serialized_dag import SerializedDagModel

            SerializedDagModel.write_dag(
                dag=lazy_dag,
                bundle_name='test-bundle',
                min_update_interval=0,
                session=session,
            )

            session.commit()

    except ImportError:
        # Airflow 2.x doesn't have the same serialization requirements
        # so this is a no-op
        pass
