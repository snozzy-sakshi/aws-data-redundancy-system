import json
import pymysql
from rapidfuzz import fuzz

RDS_HOST = 'RDS-ENDPOINT'
USERNAME = 'admin'
PASSWORD = 'Admin@123'
DATABASE = 'redundancy_system'

def lambda_handler(event, context):
    # ✅ Connect inside the handler
    connection = pymysql.connect(
        host=RDS_HOST,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )

    try:
        body = json.loads(event['body'])

        name = body['name']
        email = body['email']
        phone = body['phone']

        if not validate_email(email):
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid Email')
            }

        cursor = connection.cursor()

        query = "SELECT name, email FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            existing_name = row[0]
            existing_email = row[1]

            if existing_email == email:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Duplicate Email Found')
                }

            score = fuzz.ratio(existing_name, name)

            if score > 90:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Possible False Positive Duplicate')
                }

        insert_query = """
        INSERT INTO users(name, email, phone)
        VALUES(%s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, phone))
        connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Unique Data Inserted')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}')
        }

    finally:
        connection.close()  # ✅ Always close the connection

def validate_email(email):
    return '@' in email