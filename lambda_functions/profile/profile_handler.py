import json
import os
import base64
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from CustomExceptions.UserNotFoundException import UserNotFoundException

# Load environment
load_dotenv(dotenv_path='../.env')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.environ.get('DEFAULT_REGION')

dynamodb = boto3.resource(
    'dynamodb',
    region_name=DEFAULT_REGION
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}


def handler(event, context):
    try:
        print("Event:", event)

        if 'triggerSource' in event:
            trigger = event['triggerSource']
            if trigger == 'PostConfirmation_ConfirmSignUp':
                print(event['request']['userAttributes'])
                user_info = event['request']['userAttributes']
                user_info['userId'] = event['userName']
            response = create_user(user_info)
            if response == "OK":
                return event
            else:
                raise Exception("Can't add the user")

        # Handle Base64 decoding only if required
        if event.get("isBase64Encoded", True):
            event_body = base64.b64decode(event["body"]).decode('utf-8')
        else:
            event_body = event["body"]

        print('event body type', (event_body))
        http_method = event.get('httpMethod', '')

        if http_method == 'GET':
            print('in GET')
            query_params = event.get('queryStringParameters', {})
            email_id = query_params.get('emailId')
            user_id = query_params.get('userId')
            print("emailid and userid", email_id, user_id)
            if not email_id and not user_id:
                raise UserNotFoundException
            if email_id and user_id:
                raise Exception("Can't perform the operation.")
            if not email_id and user_id:
                return get_user_by_userid(user_id)
            print('email_id', email_id)
            return get_user_by_email(email_id)

        print('preparing event body')
        event_body = json.loads(event_body)
        if not event_body:
            raise Exception("Can't perform the operation.")

        user_info = event_body.get('userInfo')

        if not user_info:
            raise UserNotFoundException

        elif http_method == 'PATCH':
            print('in PATCH')
            return update_user(user_info)

        else:
            return response(405, {'message': 'Method Not Allowed'}, cors_headers)


    except UserNotFoundException:
        print("User not found")
        return response(400, {'message': 'User information is missing or invalid'}, cors_headers)
    except Exception as ex:
        print("Exception:", ex)
        return response(500, {'message': 'Internal server error. Contact admin.'}, cors_headers)


def get_user_by_email(emailId):
    if not emailId:
        raise UserNotFoundException

    result = table.query(
        IndexName='GSI_UserByEmailId',
        KeyConditionExpression=Key('emailId').eq(emailId)
    )
    return response(200, {'message': 'User fetched', 'data': result['Items']}, cors_headers)


def create_user(user_info):
    item = {}
    print('trigger incoming user info', user_info)

    user_id = user_info.get('userId') or user_info.get('name')
    email = user_info.get('email')

    print('userId', user_id, "email", email)
    if not user_id or not email:
        raise UserNotFoundException

    item['PK'] = f"user#{user_id}"
    item['SK'] = f"user#{email}"
    item['itemType'] = "userInfo"
    item['userId'] = user_id
    item['emailId'] = email
    item['name'] = f"{user_info.get('given_name', "")} {user_info.get('family_name', "")}"
    item["contact_num"] = user_info.get('phone_number', "")
    item["address"] = user_info.get('address', "")
    item["gender"] = user_info.get('gender', "")

    print('user_info create user', item)
    table.put_item(Item=item)
    return "OK"


def update_user(user_info):
    print('modifying user', user_info)
    email = user_info.get('emailId')
    if not email:
        raise UserNotFoundException

    # Retrieve PK/SK from existing user
    user_data = table.query(
        IndexName='GSI_UserByEmailId',
        KeyConditionExpression=Key('emailId').eq(email)
    )

    if not user_data.get('Items'):
        raise UserNotFoundException

    existing = user_data['Items'][0]

    update_expr = []
    expr_attr_vals = {}
    expr_attr_names = {}

    if 'contactnum' in user_info:
        update_expr.append("contactnum = :contactnum")
        expr_attr_vals[":contactnum"] = user_info['contactnum']

    if 'name' in user_info:
        update_expr.append("#n = :name")
        expr_attr_vals[":name"] = user_info['name']
        expr_attr_names["#n"] = "name"

    if 'contact_num' in user_info:
        update_expr.append("contact_num = :contact_num")
        expr_attr_vals[":contact_num"] = user_info['contact_num']

    if 'address' in user_info:
        update_expr.append("address = :address")
        expr_attr_vals[":address"] = user_info['address']

    update_stmt = "SET " + ", ".join(update_expr)

    table.update_item(
        Key={"PK": existing['PK'], "SK": existing['SK']},
        UpdateExpression=update_stmt,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_vals
    )

    return response(200, {'message': 'User updated successfully'}, cors_headers)


def response(status_code, body, headers=None):
    return {
        'statusCode': status_code,
        'headers': headers or {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def get_user_by_userid(user_id):
    if not user_id:
        raise UserNotFoundException
    KeyConditionExpression = Key('PK').eq(f"user#{user_id}")
    result = table.query(KeyConditionExpression=KeyConditionExpression)

    return response(200, {'message': 'User fetched', 'data': result['Items']}, cors_headers)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
