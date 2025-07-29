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
    try:
        print("Received event:", json.dumps(event))

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

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'data': listing_lookup['Items']
            },cls=DecimalEncoder)
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(ve)
            })
        }

    except Exception as ex:
        print("Unhandled exception:", ex)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Something went wrong while fetching listings: {str(ex)}"
            })
        }


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)
