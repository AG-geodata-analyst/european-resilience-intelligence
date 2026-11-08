
from datetime import datetime, timedelta, timezone
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
from sqlalchemy import create_engine

from src.ingestion.cloudflare_radar import CloudflareRadarConnector
from src.ingestion.runner import IngestionRunner

load_dotenv(".env")

def run_ingestion():
    user = os.getenv("POSTGRES_USER", "bri")
    pw   = os.getenv("POSTGRES_PASSWORD", "change_me")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB", "bri")
    engine = create_engine(f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{db}")

    connector = CloudflareRadarConnector()
    runner = IngestionRunner(engine, connector)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=2)
    
    report = runner.run(start, end)
    print(f"Ingestion complete. Raw new: {report.raw_was_new}, Events seen: {report.events_seen}, Inserted: {report.events_inserted}")

default_args = {
    'owner': 'bri',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ingest_cloudflare_outages',
    default_args=default_args,
    description='Fetch and ingest Cloudflare Radar outage data',
    schedule_interval='*/30 * * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['bri', 'ingestion'],
) as dag:
    ingest_task = PythonOperator(
        task_id='run_cloudflare_ingestion',
        python_callable=run_ingestion,
    )
