import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from CustomExceptions.UserNotFoundException import UserNotFoundException
from decimal import Decimal

load_dotenv('../.env')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

dynamodb = boto3.resource(
    'dynamodb',
    region_name=DEFAULT_REGION
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE',
    'Access-Control-Allow-Credentials': 'true',
}


def handler(event, context):
    httpMethod = event.get('httpMethod')
    try:
        if httpMethod == 'OPTIONS':
            return response(200, {'message': 'Preflight request served'}, cors_headers)

        source = None
        print("Incoming event:", json.dumps(event))
        if httpMethod == 'POST':
            source = json.loads(event.get('body'))
            if not source:
                raise ValueError("Missing request body")

        if httpMethod == 'GET':
            source = event.get('queryStringParameters', {})
            if not source:
                raise ValueError("Missing query string parameters")

        choice = source.get('choice')
        email_id = source.get('emailId')
        listing_id = source.get('listingId')

        if not email_id or not choice:
            raise ValueError("Missing required parameters: 'emailId' and 'choice'")

        # Step 1: Validate user existence
        user_lookup = table.query(
            IndexName='GSI_UserByEmailId',
            KeyConditionExpression=Key("emailId").eq(email_id)
        )

        if user_lookup.get("Count", 0) == 0:
            raise UserNotFoundException(f"User with emailId '{email_id}' not found")

        user_id = user_lookup["Items"][0]["userId"]

        if httpMethod == 'POST':
            if not listing_id:
                raise ValueError("Missing required parameter: 'listingId' to post interest")
            return handle_post_interest(listing_id, user_id)

        if httpMethod == 'GET':
            # Step 2: Route based on choice
            if choice == "interest":
                return handle_get_interest(user_id)

            elif choice == "match":
                if not listing_id:
                    raise ValueError("Missing required parameter: 'listingId' to get match")
                return handle_get_matches(listing_id)

            else:
                raise ValueError(f"Invalid choice: '{choice}' (must be 'interest' or 'match')")

    except UserNotFoundException as ex:
        return response(404, {"error": str(ex)}, cors_headers)

    except ValueError as ve:
        return response(400, {"error": str(ve)}, cors_headers)

    except Exception as e:
        print("Unhandled Exception:", e)
        return response(500, {"error": "Internal server error", "details": str(e)}, cors_headers)


def response(status_code, body, headers=None):
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def handle_post_interest(listing_id, user_id):
    item = {}
    item['PK'] = f'INTERESTS#{user_id}'
    item['SK'] = f'INTERESTS#{listing_id}'
    item['tenantId'] = user_id
    item['listingId'] = listing_id
    item['itemType'] = 'interest'

    result = table.put_item(Item=item)

    match_item = {}
    match_item['PK'] = f'MATCHES#{listing_id}'
    match_item['SK'] = f'MATCHES#{user_id}'
    match_item['listingId'] = listing_id
    match_item['tenantId'] = user_id
    match_item['ownerId'] = listing_id.split('#')[0].split('-')[0]
    print('match_item', match_item['ownerId'])
    match_item['itemType'] = 'match'

    table.put_item(Item=match_item)

    return response(200, {
        'message': "Interest recorded successfully",
    }, cors_headers)


def get_ownerId(listing_id):
    return listing_id.split('#')[0].split('-')[0]


def handle_get_interest(user_id):
    pk_userId = f'INTERESTS#{user_id}'
    print('pkuserid', pk_userId)
    query_params = {
        "IndexName": "GSI_TenantInterests",
        "KeyConditionExpression": Key("PK").eq(pk_userId)
    }

    interest_result = table.query(**query_params)
    if interest_result.get("Count", 0) == 0:
        return response(200, {'message': "No interests found", 'data': []}, cors_headers)
    listing_ids = [item['listingId'] for item in interest_result.get("Items", [])]
    print('listing ids', listing_ids)
    # use batch get to fetch listing details
    keys = [{'PK': f'LISTING#{listing_id}', 'SK': f'LISTING#{get_ownerId(listing_id)}'} for listing_id in listing_ids]

    if not keys:
        return response(200, {'message': "No interests found", 'data': []}, cors_headers)

    batch_keys = {'RequestItems': {table.name: {'Keys': keys}}}
    print('batch keys', batch_keys)
    listings_response = dynamodb.batch_get_item(**batch_keys)

    print('listings_response', listings_response)
    listings = listings_response.get('Responses', {}).get(table.name, [])
    if listings_response.get('UnprocessedKeys'):
        print("Warning: Some keys were unprocessed in batch get:", listings_response['UnprocessedKeys'])

    return response(200, {
        'message': "Interests fetched successfully",
        'data': {
            'listings': listings
        }
    }, cors_headers)


def handle_get_matches(listing_id):
    pk_listingId = f'MATCHES#{listing_id}'
    query_params = {
        "IndexName": "GSI_OwnerViewInterests",
        "KeyConditionExpression": Key("PK").eq(pk_listingId)
    }
    matches_result = table.query(**query_params)
    if matches_result.get("Count", 0) == 0:
        return response(200, {'message': "No matches found", 'data': []}, cors_headers)

    print('matches_result', matches_result)
    response_item = {}
    response_item['listingId'] = listing_id
    # get all tenant Id details from matches_result
    tenant_ids = [item['tenantId'] for item in matches_result.get("Items", [])]
    response_item['tenant_ids'] = tenant_ids

    return response(200, {
        'message': "Matches fetched successfully",
        'data': response_item
    }, cors_headers)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


