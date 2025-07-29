import os
import boto3
import base64
import json
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from CustomExceptions.UserNotFoundException import UserNotFoundException

load_dotenv('../.env')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

def handler(event, context):
    try:
        print("Incoming event:", json.dumps(event))

        body = event.get("body")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")
        event_body = json.loads(body)

        choice = event_body.get("choice")
        email_id = event_body.get("emailId")
        listing_id = event_body.get("listingId")

        if not email_id or not choice:
            raise ValueError("Missing required parameters: 'emailId' and 'choice'")

        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DEFAULT_REGION
        )
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

        # Step 1: Validate user existence
        user_lookup = table.query(
            IndexName='GSI_UserByEmailId',
            KeyConditionExpression=Key("emailId").eq(email_id)
        )

        if user_lookup.get("Count", 0) == 0:
            raise UserNotFoundException(f"User with emailId '{email_id}' not found")

        user_id = user_lookup["Items"][0]["userId"]

        httpMethod = event.get('httpMethod')
        if httpMethod == 'POST':
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
            match_item['ownerId'] = listing_id.split('#')[0]
            match_item['itemType'] = 'match'

            update_match = table.put_item(Item=match_item)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': "Interest recorded successful",
                    'data': result
                })
            }

        if httpMethod == 'GET':
            # Step 2: Route based on choice
            if choice == "interest":
                pk_userId = f'INTERESTS#{user_id}'
                print('pkuserid',pk_userId)
                query_params = {
                    "IndexName": "GSI_TenantInterests",
                    "KeyConditionExpression": Key("PK").eq(pk_userId)
                }

            elif choice == "match":
                if not listing_id:
                    raise ValueError("Missing required parameter: 'listingId' for match")
                pk_listingId = f'MATCHES#{listing_id}'
                query_params = {
                    "IndexName": "GSI_OwnerViewInterests",
                    "KeyConditionExpression": Key("PK").eq(pk_listingId)
                }

            else:
                raise ValueError(f"Invalid choice: '{choice}' (must be 'interest' or 'match')")

            query_result = table.query(**query_params)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': "Query successful",
                    'data': query_result.get("Items", [])
                })
            }

    except UserNotFoundException as ex:
        return {
            'statusCode': 404,
            'body': json.dumps({"error": str(ex)})
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(ve)})
        }

    except Exception as e:
        print("Unhandled Exception:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Internal server error", "details": str(e)})
        }
