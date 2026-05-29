from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default settings for our robotic schedule
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG (The Schedule)
with DAG(
    'oracle_dbt_attribution_pipeline',
    default_args=default_args,
    description='Automates the dbt Silver and Gold models in Oracle ADW',
    schedule_interval=timedelta(hours=1), # Runs automatically every 1 hour
    catchup=False,
    tags=['marketing', 'attribution', 'oracle']
) as dag:

    # The actual task we want Airflow to execute
    run_dbt_models = BashOperator(
        task_id='run_dbt_models',
        bash_command="""
            source /home/opc/attribution-pipeline/venv/bin/activate && \
            export TNS_ADMIN=/home/opc/attribution-pipeline/config/wallet && \
            export WALLET_LOCATION=/home/opc/attribution-pipeline/config/wallet && \
            export WALLET_PASSWORD="Preman901202!" && \
            cd /home/opc/attribution-pipeline/attribution_models && \
            dbt run
        """
    )

    # If we had more tasks (like sending a Slack alert), we would chain them here
    run_dbt_models
