# Reddit ETL Pipeline with Apache Airflow, AWS Glue, and Redshift

This project demonstrates a complete end-to-end ETL pipeline that extracts data from the Reddit API and processes it through multiple services including Apache Airflow, AWS S3, AWS Glue, and Amazon Redshift using a serverless architecture. The pipeline is containerized using Docker and orchestrated using Airflow.

## 🚀 Project Overview

**Objective:**  
To extract data from the Reddit API, transform it using AWS Glue, and load it into Amazon Redshift using a Lambda-triggered COPY command.

---

## 🧩 Architecture Overview

Reddit API → Airflow → S3 (raw) → AWS Glue → S3 (processed) → Lambda → Redshift


---

## 📦 Components and Steps

### 1. **Docker & Apache Airflow Setup**
- Used **Docker Desktop** to create a local environment for Apache Airflow.

### 2. **Airflow DAG**
- Created a DAG with three main tasks:
  - **Extract**: Fetch data from Reddit API using `praw`.
  - **Upload**: Store the response as a JSON file and upload to an S3 bucket.
  - **Trigger Glue**: Initiate an AWS Glue job to process the uploaded data.

### 3. **Reddit API Integration**
- Used the `praw` Python library to pull data (e.g., posts, comments) from Reddit.
- Saved the extracted data as JSON in a structured format locally.

### 4. **AWS CLI and Boto3 Integration**
- Configured AWS CLI locally with proper credentials and default region.
- Used `boto3` to upload raw JSON files to an S3 bucket.

### 5. **AWS Glue**
- Created an AWS Glue job to:
  - Read JSON from the `raw/` S3 folder.
  - Convert and clean the data using Spark.
  - Output a CSV to a `processed/` folder in S3.

### 6. **Amazon Redshift Serverless**
- Configured an Amazon Redshift **Serverless** workgroup. 
- Created target table for storing the processed Reddit data.

### 7. **AWS Lambda**
- Created a Lambda function to execute a `COPY` command using the **Redshift Data API**.
- The function runs when a file lands in the `processed/` folder in S3.

### 8. **Lambda Trigger**
- Set up an **S3 Event Notification** to trigger the Lambda function automatically upon file upload by Glue.

---

## 📁 Folder Structure

```bash
reddit-etl-pipeline/
│
├── dags/
│   └── tasks.py                        # Airflow DAG script
│   └── data/                      
│       └── reddit_posts.json           # Raw JSON data from the API
|   
├── glue_job/
│   └── reddit_json_to_csv.py           # Script for converting JSON into CSV and upload to S3
│
├── lambda_function/
│   └── copy_from_s3_to_redshift.py     # COPY command trigger for Redshift
│
├── docker-compose.yaml                 # Airflow container orchestration
├── .env                                # Airflow environment variables
├── requirements.txt                    # Python modules
└── README.md                           # Project documentation
