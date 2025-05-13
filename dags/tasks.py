import os
import praw
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3

# Load variables from .env file
load_dotenv(dotenv_path = 'opt/airflow/.env')

# Get posts data from Reddit API
def get_reddit_posts():
    reddit = praw.Reddit(
        client_id = "dk8Av7gxlcovpTtaCO0Exg",
        client_secret = "Q3We3O6Zb3SrW9WfWIFmHvbmnsVFEA",
        user_agent = "RedditETL/0.1 by u/Ajaikumar_A"
    )

    posts = []

    for post in reddit.subreddit("dataengineering").hot(limit = 1000):
        posts.append(
            {
                "title": post.title, 
                "score": post.score, 
                "url": post.url, 
                "created_utc": post.created_utc, 
                "no_of_comments": post.num_comments
            }
        )

    df = pd.DataFrame(posts)

    # Create output directory if it doesn't exist
    output_dir = "/opt/airflow/dags/data"
    os.makedirs(output_dir, exist_ok = True)

    df.to_json(os.path.join(output_dir, "reddit_posts.json"), orient = "records")

# Upload the API response data to S3
def upload_to_s3():
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        Filename = "/opt/airflow/dags/data/reddit_posts.json", 
        Bucket = "project-reddit-etl", 
        Key = "raw/reddit_posts.json"
    )

# Trigger Glue job for converting JSON to Parquet in S3
def trigger_glue_job(job_name, arguments):
    glue_client = boto3.client('glue')

    try:
        response = glue_client.start_job_run(
            JobName = job_name, 
            Arguments = arguments
        )
        print(f"Glue job '{job_name}' triggered successfully.")
    except Exception as e:
        print(f"Error triggering Glue job: {e}")
        raise 

with DAG(
    dag_id = "get_reddit_posts", 
    start_date = datetime(2025, 4, 30), 
    schedule_interval = "@daily", 
    catchup = False
) as dag:
    save_task = PythonOperator(
        task_id = "save_reddit_posts", 
        python_callable = get_reddit_posts
    )

    upload_task = PythonOperator(
        task_id = "upload_to_s3",
        python_callable = upload_to_s3
    )
    
    trigger_glue_job_task = PythonOperator(
        task_id = "trigger_glue_job", 
        python_callable = trigger_glue_job, 
        op_kwargs = {
            'job_name': 'reddit_json_to_parquet', 
            'arguments': {
                '--input_path': 's3://project-reddit-etl/raw/reddit_posts.json', 
                '--output_path': 's3://project-reddit-etl/processed/'
            }
        }
    )


    save_task >> upload_task >> trigger_glue_job_task