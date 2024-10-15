import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator


dag = DAG("data_pipeline_dag", description="Causaly Data Pipeliine DAG")

# Make sure scripts are executable
os.environ["PYTHONPATH"] = "/opt/src"


t1 = BashOperator(
    task_id="create_sqlite_db",
    bash_command="python /opt/src/data_pipeline_app/stages/create_db.py",
    dag=dag,
)
t2 = BashOperator(
    task_id="store_keyword_pair_occurrences",
    bash_command="python /opt/src/data_pipeline_app/stages/keyword_co_occurrence_pairs.py",
    dag=dag,
)

t3 = BashOperator(
    task_id="aggregate_keyword_pairs",
    bash_command="python /opt/src/data_pipeline_app/stages/calculate_aggregates.py",
    dag=dag,
)

t1 >> t2 >> t3
