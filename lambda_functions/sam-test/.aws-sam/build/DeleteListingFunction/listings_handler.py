import base64
import json
import os
import uuid
import boto3
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from requests_toolbelt.multipart import decoder
from CustomExceptions.UserNotFoundException import UserNotFoundException

load_dotenv(dotenv_path='../.env')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')

def handler(event, context):
    try:
        body = base64.b64decode(event["body"]) if event.get('isBase64Encoded') else event["body"].encode()
        content_type = event.get('headers', {}).get('Content-Type')
        parser = decoder.MultipartDecoder(body, content_type)

        rental_info, home_tour_file = None, None

        for part in parser.parts:
            disposition = part.headers.get(b"Content-Disposition", b"").decode()
            if "name=\"rentalInfo\"" in disposition:
                rental_info = json.loads(part.text)
            elif "name=\"homeTour\"" in disposition:
                home_tour_file = {
                    "filename": str(uuid.uuid4()),
                    "content": part.content
                }

        if not rental_info:
            raise ValueError("Missing rentalInfo in form data.")

        # Initialize DynamoDB
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DEFAULT_REGION
        )
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

        email_id = rental_info.get("emailId")
        user_lookup = table.query(
            IndexName="GSI_UserByEmailId",
            KeyConditionExpression=Key("emailId").eq(email_id)
        )

        if user_lookup.get('Count', 0) == 0:
            raise UserNotFoundException(f"No user found with email: {email_id}")

        rental_info["userId"] = user_lookup["Items"][0]["userId"]

        if event['httpMethod'] == 'POST':
            item = prepare_data(rental_info)
            table.put_item(Item=item)
            return build_response(201, "Listing created successfully")

        elif event['httpMethod'] == 'PUT':
            update_stmt = prepare_update_statement(rental_info)
            table.update_item(
                Key={
                    'PK': f"LISTING#{rental_info['listingId']}",
                    'SK': f"LISTING#{rental_info['userId']}"
                },
                **update_stmt,
                ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
            )
            return build_response(200, "Listing updated successfully")

        else:
            return build_response(405, "Method not allowed")

    except Exception as ex:
        print("Exception:", ex)
        return build_response(500, f"Internal error: {str(ex)}")


def prepare_data(rental_info):
    listing_id = f"{rental_info['userId']}-{uuid.uuid4()}"
    rental = rental_info["rentalInformation"]
    full_address = f"{rental['address1']}, {rental['address2']}, {rental['area']}, {rental['district']}, {rental['state']}, {rental['pincode']}"

    return {
        "PK": f"LISTING#{listing_id}",
        "SK": f"LISTING#{rental_info['userId']}",
        "listingId": listing_id,
        "ownerId": rental_info["userId"],
        "itemType": "listing",
        "SearchItem": f"LISTING#{rental['state']}",
        "bhk": rental["beds"],
        "rpm": rental["rpm"],
        "occupantType": rental["occupantType"],
        "dateAvailable": rental["dateAvailable"],
        "state": rental["state"],
        "district": rental["district"],
        "area": rental["area"],
        "rentalInformation": {
            "address": full_address,
            "beds": rental["beds"],
            "baths": rental["baths"],
            "balcony": rental["balconies"],
            "facing": rental["facing"],
            "floor": rental["floor"],
            "maxOccupants": rental["maxOccupants"],
            "waterAvailability": rental["waterAvailability"],
            "hasElevator": rental["hasElevator"],
            "hasBorewell": rental["hasBorewell"],
            "utilities": rental_info["utilities"],
            "amenities": rental_info["amenities"]
        },
        "highlights": rental_info["highlights"],
        "leaseTerms": rental_info["leaseTerms"]
    }

def prepare_update_statement(rental_info):
    rental = rental_info["rentalInformation"]
    full_address = f"{rental['address1']}, {rental['address2']}, {rental['area']}, {rental['district']}, {rental['state']}, {rental['pincode']}"

    expr_attr_vals = {
        ":bhk": rental["beds"],
        ":rpm": rental["rpm"],
        ":occupantType": rental["occupantType"],
        ":dateAvailable": rental["dateAvailable"],
        ":district": rental["district"],
        ":area": rental["area"],
        ":full_address": full_address,
        ":beds": rental["beds"],
        ":baths": rental["baths"],
        ":balconies": rental["balconies"],
        ":facing": rental["facing"],
        ":floor": rental["floor"],
        ":maxOccupants": rental["maxOccupants"],
        ":waterAvailability": rental["waterAvailability"],
        ":hasElevator": rental["hasElevator"],
        ":hasBorewell": rental["hasBorewell"],
        ":utilities": rental_info["utilities"],
        ":amenities": rental_info["amenities"],
        ":highlights": rental_info["highlights"],
        ":leaseTerms": rental_info["leaseTerms"]
    }

    update_expr = (
        "SET bhk = :bhk, rpm = :rpm, occupantType = :occupantType, "
        "dateAvailable = :dateAvailable, district = :district, area = :area, "
        "rentalInformation.address = :full_address, rentalInformation.beds = :beds, "
        "rentalInformation.baths = :baths, rentalInformation.balconies = :balconies, "
        "rentalInformation.facing = :facing, rentalInformation.floor = :floor, "
        "rentalInformation.maxOccupants = :maxOccupants, "
        "rentalInformation.waterAvailability = :waterAvailability, "
        "rentalInformation.hasElevator = :hasElevator, rentalInformation.hasBorewell = :hasBorewell, "
        "rentalInformation.utilities = :utilities, rentalInformation.amenities = :amenities, "
        "highlights = :highlights, leaseTerms = :leaseTerms"
    )

    return {
        "UpdateExpression": update_expr,
        "ExpressionAttributeValues": expr_attr_vals
    }

def build_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "message": message
        })
    }