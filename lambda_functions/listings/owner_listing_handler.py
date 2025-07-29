import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv(dotenv_path='../.env')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')

def handler(event, context):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }
    try:
        print("Received event:", json.dumps(event))

        if (event.get('httpMethod') == 'OPTIONS') :
            return response(200,
        {
            'message': 'Search completed',
            'result': 'CORS preflight successfully fetched'
        },
            headers=cors_headers)

        query_params = event.get('queryStringParameters') or {}
        email_id = query_params.get('emailId')

        if not email_id:
            raise ValueError("Missing required query parameter: emailId")

        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DEFAULT_REGION
        )
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

        # Step 1: Get user info from email
        user_lookup = table.query(
            IndexName='GSI_UserByEmailId',
            KeyConditionExpression=Key('emailId').eq(email_id)
        )

        if user_lookup.get('Count', 0) == 0:
            raise ValueError(f"No user found for emailId: {email_id}")

        user_id = user_lookup['Items'][0]['userId']

        # Step 2: Get listings by owner
        listing_lookup = table.query(
            IndexName='GSI_ListingsByOwner',
            KeyConditionExpression=Key('ownerId').eq(user_id),
            FilterExpression=Attr('itemType').eq('listing')
        )

        message = (
            "You don't have any listings posted."
            if listing_lookup.get('Count', 0) == 0
            else "Fetched user listings successfully"
        )

        return response(200, {
                'message': message,
                'data': listing_lookup['Items']
            })

    except ValueError as ve:
        return response(400,{
                'error': str(ve)
            }, headers= cors_headers)

    except Exception as ex:
        print("Unhandled exception:", ex)
        return response(500, {
            'error': f"Something went wrong while fetching listings: {str(ex)}"
            }, headers=cors_headers)

def response(status_code, body, headers=None):
    return {
        'statusCode': status_code,
        'headers': headers or {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)
