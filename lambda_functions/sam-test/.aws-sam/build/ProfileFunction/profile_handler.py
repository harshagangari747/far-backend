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

def handler(event, context):
    try:
        print("Event:", event)

        # Handle Base64 decoding only if required
        if event.get("isBase64Encoded", False):
            event_body = base64.b64decode(event["body"]).decode('utf-8')
        else:
            event_body = event["body"]

        event_body = json.loads(event_body)
        user_info = event_body.get('userInfo')

        if not user_info:
            raise UserNotFoundException

        http_method = event.get('httpMethod', '')

        if http_method == 'GET':
            return get_user_by_email(user_info)

        elif http_method == 'POST':
            return create_user(user_info)

        elif http_method == 'PATCH':
            return update_user(user_info)

        else:
            return response(405, {'message': 'Method Not Allowed'})

    except UserNotFoundException:
        return response(400, {'message': 'User information is missing or invalid'})
    except Exception as ex:
        print("Exception:", ex)
        return response(500, {'message': 'Internal server error. Contact admin.'})

def get_user_by_email(user_info):
    email = user_info.get('emailId')
    if not email:
        raise UserNotFoundException

    result = table.query(
        IndexName='GSI_UserByEmailId',
        KeyConditionExpression=Key('emailId').eq(email)
    )
    return response(200, {'message': 'User fetched', 'data': result['Items']})

def create_user(user_info):
    user_id = user_info.get('userId') or user_info.get('name')
    email = user_info.get('emailId')

    print('userId',user_id,"email",email)
    if not user_id or not email:
        raise UserNotFoundException

    user_info['PK'] = f"user#{user_id}"
    user_info['SK'] = f"user#{email}"
    user_info['itemType'] = "userInfo"
    user_info['userId'] = user_id
    user_info['emailId'] = email

    print('user_info create user',user_info)
    table.put_item(Item=user_info)
    return response(201, {'message': 'User created successfully'})

def update_user(user_info):
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

    update_stmt = "SET " + ", ".join(update_expr)

    table.update_item(
        Key={"PK": existing['PK'], "SK": existing['SK']},
        UpdateExpression=update_stmt,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_vals
    )

    return response(200, {'message': 'User updated successfully'})

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
