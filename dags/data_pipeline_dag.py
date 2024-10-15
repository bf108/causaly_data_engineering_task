import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator


dag = DAG("postgres_dag", description="Causaly Data Pipeline DAG")

# Make sure scripts are executable
os.environ["PYTHONPATH"] = "/opt/src"


t1 = BashOperator(
    task_id="populate_keyword_pairs_postgres",
    bash_command="python /opt/src/data_pipeline_app/stages/keyword_co_occurrence_pairs.py",
    dag=dag,
)

t2 = BashOperator(
    task_id="query_keyword_pairs_postgres",
    bash_command="python /opt/src/data_pipeline_app/stages/query_keyword_pairs_table.py",
    dag=dag,
)


t3 = BashOperator(
    task_id="aggregate_keyword_pairs_postgres",
    bash_command="python /opt/src/data_pipeline_app/stages/calculate_aggregates.py",
    dag=dag,
)

t1 >> t2 >> t3
