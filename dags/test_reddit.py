import os
import praw
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path = 'opt/airflow/.env')

def get_reddit_posts():
    reddit = praw.Reddit(
        client_id = os.getenv("REDDIT_CLIENT_ID"),
        client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent = os.getenv("REDDIT_USER_AGENT")
    )

    posts = []

    for post in reddit.subreddit("dataengineering").hot(limit=5):
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

    df.to_csv(os.path.join(output_dir, "reddit_posts.csv"), index = False)

with DAG(
    dag_id = "get_reddit_posts", 
    start_date = datetime(2025, 4, 30), 
    schedule_interval = "@daily", 
    catchup = False
) as dag:
    task = PythonOperator(
        task_id = "run_etl", 
        python_callable = get_reddit_posts
    )