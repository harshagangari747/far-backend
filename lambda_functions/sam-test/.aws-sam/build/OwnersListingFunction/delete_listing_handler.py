import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from CustomExceptions.QueryStringParamNotFoundException import QueryStringParamNotFoundException

load_dotenv('../.env')

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')

def handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        request_query = event.get('queryStringParameters')
        if not request_query:
            raise QueryStringParamNotFoundException("Missing query string parameters")

        owner_id = request_query.get('ownerId')
        listing_id = request_query.get('listingId')

        if not owner_id or not listing_id:
            raise ValueError("Both ownerId and listingId must be provided")

        key = {
            'PK': f'LISTING#{listing_id}',
            'SK': f'LISTING#{owner_id}'
        }

        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DEFAULT_REGION
        )
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

        print("Deleting with key:", key)

        result = table.delete_item(Key=key)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Listing with ID '{listing_id}' deleted successfully"
            })
        }

    except QueryStringParamNotFoundException as qex:
        print("Query param error:", qex)
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(qex)
            })
        }

    except Exception as ex:
        print("Unexpected error:", ex)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Failed to delete listing: {str(ex)}"
            })
        }
