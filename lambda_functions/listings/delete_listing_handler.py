import os
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv
from CustomExceptions.QueryStringParamNotFoundException import QueryStringParamNotFoundException

load_dotenv('../.env')

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')

dynamodb = boto3.resource(
    'dynamodb',
    region_name=DEFAULT_REGION
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def handler(event, context):
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
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

        print("Deleting with key:", key)

        interests_of_listing = get_interests_of_listing(listing_id)
        print("Interests of listing:", interests_of_listing)
        matches_of_listing = get_matches_of_listing(listing_id)
        print("Matches of listing:", matches_of_listing)
        # Perform transact delete operation

        with table.batch_writer() as batch:
            batch.delete_item(Key=key)

            for interest in interests_of_listing:
                batch.delete_item(Key={
                    'PK': interest['PK'],
                    'SK': interest['SK']
                })

            for match in matches_of_listing:
                batch.delete_item(Key={
                    'PK': match['PK'],
                    'SK': match['SK']
                })

        return response(200,
                        {'message': f"Listing with ID '{listing_id}' deleted successfully"}, cors_headers)


    except QueryStringParamNotFoundException as qex:
        print("Query param error:", qex)
        return response(400, {'error': str(qex)}, cors_headers)

    except Exception as ex:
        print("Unexpected error:", ex)
        return response(500, {'error': f"Unexpected error: {str(ex)}"}, cors_headers)


def response(status_code, body, headers=None):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': headers or {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    }


def get_interests_of_listing(listing_id):
    print('Getting interests...')
    response = table.query(
        IndexName='GSI_GetInterestOfListing',
        KeyConditionExpression=Key('itemType').eq('interest'),
        FilterExpression=Attr('listingId').eq(listing_id)
    )
    return response['Items']


def get_matches_of_listing(listing_id):
    print('Getting matches...')
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'MATCHES#{listing_id}')
    )
    return response['Items']
