import json
import os
import base64
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv

from CustomExceptions.QueryStringParamNotFound import QueryStringParamNotFound
from CustomExceptions.SearchByStateFoundEmptyException import SearchByStateFoundEmptyException
from CustomExceptions.NoResultsFoundException import NoResultsFoundException

load_dotenv(dotenv_path='../.env')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.environ.get('DEFAULT_REGION')

def handler(event, context):
    try:
        # print("Incoming event:", event)
        query_params = None
        search_key = None
        filters = []
        print('** listing', event)

        # Parse query string for listingId lookup
        query_string_params = event.get('queryStringParameters', {})

        if query_string_params:
            listing_id = query_string_params.get('listingId')
            query_params = {
                'IndexName': 'GSI_GetListingsById',
                'KeyConditionExpression': Key('PK').eq(f'LISTING#{listing_id}')
            }

        # If not listingId, parse body for filter-based search
        elif event.get('body'):
            body = event['body']
            if event.get("isBase64Encoded", False):
                body = base64.b64decode(body).decode('utf-8')
            event_body = json.loads(body)
            search_query = event_body.get('searchQuery', {})
            print('search query',search_query)

            state = search_query.get('state')
            print(event_body,state)
            if not state:
                raise SearchByStateFoundEmptyException("State parameter should not be empty")
            search_key = f"LISTING#{state}"

            if district := search_query.get('district'):
                filters.append(Attr('district').eq(district))
            if area := search_query.get('area'):
                filters.append(Attr('area').eq(area))
            if rpm := search_query.get('rpm'):
                filters.append(Attr('rpm').lte(int(rpm)))
            if bhk := search_query.get('bhk'):
                filters.append(Attr('bhk').lte(int(bhk)))
            if occupant_type := search_query.get('occupantType'):
                filters.append(Attr('occupantType').eq(occupant_type))

            query_params = {
                'IndexName': 'GSI_SearchByState',
                'KeyConditionExpression': Key('SearchItem').eq(search_key)
            }

            if filters:
                filter_expression = filters[0]
                for condition in filters[1:]:
                    filter_expression = filter_expression & condition
                query_params['FilterExpression'] = filter_expression

        else:
            raise QueryStringParamNotFound("Please include listingId or search using filters")

        # DynamoDB query
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DEFAULT_REGION
        )
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        result = table.query(**query_params)

        if result.get('Count') == 0:
            raise NoResultsFoundException("Search yielded no results")

        return response(200, {
            'message': 'Search completed',
            'result': result['Items']
        })

    except (SearchByStateFoundEmptyException, QueryStringParamNotFound, NoResultsFoundException) as e:
        return response(404, {'message': str(e)})
    except Exception as e:
        print("Unhandled exception:", e)
        return response(500, {'message': 'Something went wrong. Contact admin.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body, cls=DecimalEncoder)
    }


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
