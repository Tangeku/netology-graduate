from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import datetime, timedelta
from tasks.etl_store.extract_data_nds import dim_nds
from tasks.etl_store.part_sql import (
    generate_tables_dds,
    update_dds_tables,
    generate_schema,
    update_dds_fact,
)


default_args = {
}

with DAG(
    dag_id='etl_store',
    start_date=datetime(2024, 7, 1),
    schedule_interval='0 1 * * *',
    default_args=default_args,
    catchup=False,
) as dag:
    
    start = EmptyOperator(task_id='start')

    schema_create_task = PostgresOperator(
        task_id='schema_create',
        postgres_conn_id='postgres-netology',
        sql=generate_schema,
    )

    nds_load_task = PythonOperator(
        task_id='nds-load',
        python_callable=dim_nds,
        op_kwargs={"hook":PostgresHook(postgres_conn_id='postgres-netology')},
    )

    dds_create_task = PostgresOperator(
        task_id='dds-create',
        postgres_conn_id='postgres-netology',
        sql=generate_tables_dds,
    )

    dds_dim_load_task = PostgresOperator(
        task_id='dds-dim-load',
        postgres_conn_id='postgres-netology',
        sql=update_dds_tables,
    )

    dds_fact_load_task = PostgresOperator(
        task_id='dds-load',
        postgres_conn_id='postgres-netology',
        sql=update_dds_fact,
    )

    start >> schema_create_task >> nds_load_task >> dds_create_task >> dds_dim_load_task >> dds_fact_load_task