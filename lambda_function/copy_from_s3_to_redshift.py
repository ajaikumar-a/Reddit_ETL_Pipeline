import json
import  boto3
import os
import time
from urllib import parse

redshift_data = boto3.client("redshift-data")

REDSHIFT_DATABASE = os.environ['REDSHIFT_DATABASE']
REDSHIFT_WORKGROUP = os.environ['REDSHIFT_WORKGROUP']
REDSHIFT_ROLE = os.environ['REDSHIFT_ROLE']
REDSHIFT_USER = os.environ['REDSHIFT_USER']

def lambda_handler(event, context):
    key = 's3://project-reddit-etl/processed/'

    redshift_command = f'''
    COPY reddit_etl_project.posts
    FROM '{key}'
    IAM_ROLE '{REDSHIFT_ROLE}'
    FORMAT AS CSV
    IGNOREHEADER 1
    DELIMITER ','
    '''
    print(redshift_command)
    response = redshift_data.execute_statement(
        Database = REDSHIFT_DATABASE,
        WorkgroupName = REDSHIFT_WORKGROUP,
        Sql = redshift_command
    )
    print(response)
    
    statement_id = response['Id']
    print(f"Redshift statement submitted with ID: {statement_id}")

    # Poll for the statement to complete
    status = 'STARTED'
    while status in ['STARTED', 'SUBMITTED', 'PICKED']:
        time.sleep(5)
        desc_response = redshift_data.describe_statement(Id = statement_id)
        status = desc_response['Status']
        print(f"Redshift statement status: {status}")

        if status == 'FAILED':
            error_message = desc_response.get('Error', 'Unknown error')
            print(f"Redshift statement failed: {error_message}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"Redshift statement failed: {error_message}")
            }
        elif status == 'FINISHED':
            print("Redshift statement finished successfully")
            return {
                'statusCode': 200,
                'body': json.dumps('Redshift statement finished successfully')
            }
            