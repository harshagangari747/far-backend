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

dynamodb = boto3.resource(
    'dynamodb',
    region_name=DEFAULT_REGION
)

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def handler(event, context):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }

    try:
        if (event.get('httpMethod') == 'OPTIONS'):
            return response(200,
                            {
                                'message': 'Search completed',
                                'result': 'CORS preflight successfully fetched'
                            },
                            headers=cors_headers)

        # print("Incoming event:", event)
        query_params = None
        search_key = None
        filters = []

        print('updated function to use query params', event)

        # Parse query string for listingId lookup
        query_string_params = event.get('queryStringParameters', {})

        if query_string_params:
            listing_id = query_string_params.get('listingId')
            if listing_id:
                query_params = {
                    'IndexName': 'GSI_GetListingsById',
                    'KeyConditionExpression': Key('PK').eq(f'LISTING#{listing_id}')
                }
            else:
                state = query_string_params.get('state')
                district = query_string_params.get('district')
                area = query_string_params.get('area')
                bhk = query_string_params.get('bhk')
                rpm = query_string_params.get('rpm')
                occupant_type = query_string_params.get('occupantType')
                print('state', state, 'district', district, 'area', area, 'bhk', bhk, 'rpm', rpm, 'occupantType',
                      occupant_type)

                # If not listingId, parse body for filter-based search

                if not state:
                    raise SearchByStateFoundEmptyException("State parameter should not be empty")
                search_key = f"LISTING#{state}"

                if district:
                    print('adding district filter')
                    filters.append(Attr('district').eq(district))
                if area:
                    print('adding area filter')
                    filters.append(Attr('area').eq(area))
                if rpm:
                    print('adding rpm filter')
                    filters.append(Attr('rpm').lte(int(rpm)))
                if bhk:
                    print('adding bhk filter')
                    filters.append(Attr('bhk').lte(int(bhk)))
                if occupant_type:
                    print('adding occupant type filter')
                    filters.append(Attr('occupantType').eq(occupant_type))

                print('filter exp', filters)

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
        result = table.query(**query_params)
        print('result', result)

        if result.get('Count') == 0:
            raise NoResultsFoundException("Search yielded no results")

        return response(200,
                        {
                            'message': 'Search completed',
                            'result': result['Items']
                        },
                        headers=cors_headers)

    except (SearchByStateFoundEmptyException, QueryStringParamNotFound, NoResultsFoundException) as e:
        return response(404, {'message': str(e)})
    except Exception as e:
        print("Unhandled exception:", e)
        return response(500, {'message': 'Something went wrong. Contact admin.'})


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
            return float(obj)
        return super().default(obj)
