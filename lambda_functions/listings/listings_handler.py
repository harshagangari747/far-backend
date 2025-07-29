import base64
import json
import os
import uuid
import boto3
import io
from decimal import Decimal
from datetime import datetime, date
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from requests_toolbelt.multipart import decoder
from CustomExceptions.UserNotFoundException import UserNotFoundException

load_dotenv(dotenv_path='../.env')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEFAULT_REGION = os.getenv('DEFAULT_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
CLOUDFRONT_DISTRIBUTION = os.getenv('CLOUDFRONT_DISTRIBUTION')

dynamodb = boto3.resource('dynamodb', region_name=DEFAULT_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

lambda_client = boto3.client('lambda', region_name=DEFAULT_REGION)


def handler(event, context):
    print('event', event)
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*"
    }

    if event.get('httpMethod') == 'OPTIONS':
        return build_response(200, "Success", cors_headers)

    try:
        # if not event.get('isBase64Encoded'):
        #     raise ValueError("Request body is not Base64 encoded. Ensure 'multipart/form-data' is configured as a binary type in API Gateway.")
        if event.get('isBase64Encoded'):
            body = base64.b64decode(event["body"])
        else:
            body = event["body"].encode('utf-8  ')
        # body = base64.b64decode(event["body"])
        print('body', body)
        content_type = event.get('headers', {}).get('content-type') or event.get('headers', {}).get('Content-Type')
        parser = decoder.MultipartDecoder(body, content_type)

        rental_info = None
        image_files = []

        for part in parser.parts:
            print('part headers', part.headers)
            disposition = part.headers.get(b"Content-Disposition", b"").decode()
            if "name=\"rentalInfo\"" in disposition:
                rental_info = json.loads(part.text)
            elif "name=\"homeTour\"" in disposition:
                filename = extract_filename(disposition)
                if filename:
                    # <<< FIX: Ensure content_type is decoded to a string when stored
                    content_type_bytes = part.headers.get(b"Content-Type", b"image/jpeg")
                    image_files.append({
                        "filename": filename,
                        "content": part.content,  # This is raw bytes, which is correct
                        "content_type": content_type_bytes.decode('utf-8'),  # Store as string
                        "size": len(part.content)
                    })
                    print('content first 20 bytes:', part.content[:20])

        if not rental_info:
            raise ValueError("Missing rentalInfo in form data.")
        print('passing to validation code')
        isValidRentalListing = validate_listing_info(rental_info)
        print('isValidRentalListing', isValidRentalListing)
        print('Validation passed')

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
            item["homeTour"] = get_uploaded_image_urls(image_files, rental_info["userId"], item["listingId"])
            print('item homeTour urls', item['homeTour'])
            table.put_item(Item=item)
            print('added item', item)
            return build_response(201, {
                "message": "Listing created successfully",
                "listingId": item
            }, cors_headers)

        elif event['httpMethod'] == 'PUT':
            print('updating listing')
            image_urls = get_uploaded_image_urls(image_files, rental_info["userId"], rental_info["listingId"])
            rental_info["homeTour"] = image_urls
            print('updated homeTour urls', rental_info['homeTour'])

            update_stmt = prepare_update_statement(rental_info)
            table.update_item(
                Key={
                    'PK': f"LISTING#{rental_info['listingId']}",
                    'SK': f"LISTING#{rental_info['userId']}"
                },
                **update_stmt,
                ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
            )
            print('update success of listingid', rental_info['listingId'])
            updated_item = table.get_item(
                Key={
                    'PK': f"LISTING#{rental_info['listingId']}",
                    'SK': f"LISTING#{rental_info['userId']}"
                }
            )
            print('updated item', updated_item.get('Item'))
            return build_response(200, {"message": "Listing updated successfully",
                                        "listing": updated_item.get('Item')}, cors_headers)

        else:
            return build_response(405, "Method not allowed", cors_headers)

    except MalformedValuesException as ve:
        print("Malformed input:", ve)
        message = 'One or more input values have inacceptable values. Please check again'
        return build_response(400, str(message), cors_headers)

    except Exception as ex:
        print("Exception:", ex)
        return build_response(500, f"Internal error: {str(ex)}", cors_headers)


def get_uploaded_image_urls(files, prefix, listing_id):
    print('uploading images')
    s3 = boto3.client('s3')
    urls = []
    accepted_extensions = {'png', 'jpg', 'jpeg'}
    files_to_process = []

    for idx, file in enumerate(files):
        # The filename might contain spaces or special characters, so we create a safer key name
        safe_filename = f"image_{idx}_{uuid.uuid4()}"
        file_extension = file['filename'].split('.')[-1]

        if file_extension.lower() not in accepted_extensions:
            raise MalformedValuesException(
                f"Unsupported file type: {file_extension}. Only .png, .jpg, and .jpeg are allowed.")

        file_extension = file['filename'].split('.')[-1] if '.' in file['filename'] else 'jpg'
        file_key = f"hometour/{prefix}/{listing_id}/{safe_filename}.{file_extension}"
        files_to_process.append((file_key, file['content'], file['content_type']))

    for file_key, content, content_type in files_to_process:
        print(f"Uploading {file_key} with content type: {content_type}")
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_key,
            Body=content,
            ContentType=content_type
        )
        urls.append(f"https://{CLOUDFRONT_DISTRIBUTION}/{file_key}")
    print("Generated URLs:", urls)
    return urls


# No changes needed for the functions below, but they are included for completeness
def extract_filename(disposition):
    for part in disposition.split(';'):
        if part.strip().startswith("filename="):
            return part.split("=")[1].strip("\"")
    return f"{uuid.uuid4()}.jpg"


def prepare_data(rental_info):
    # ... (no changes from your original code)
    print('preparing post data')
    listing_id = f"{rental_info['userId']}-{uuid.uuid4()}"
    rental = rental_info["rentalInformation"]
    full_address = f"{rental['address1']}, {rental.get('address2', '')}, {rental['area']}, {rental['district']}, {rental['state']}, {rental['pincode']}"

    return {
        "PK": f"LISTING#{listing_id}",
        "SK": f"LISTING#{rental_info['userId']}",
        "listingId": listing_id,
        "ownerId": rental_info["userId"],
        "itemType": "listing",
        "SearchItem": f"LISTING#{rental['state']}",
        "bhk": int(rental["beds"]),
        "rpm": int(rental["rpm"]),
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
            "utilities": rental["utilities"],
            "amenities": rental["amenities"]
        },
        "highlights": rental_info["highlights"],
        "leaseTerms": rental_info["leaseTerms"]
    }


def prepare_update_statement(rental_info):
    # ... (no changes from your original code, though you have a typo "rentalInformation.highlights")
    print('preparing update statement')
    rental = rental_info["rentalInformation"]
    full_address = f"{rental['address1']}, {rental.get('address2', '')}, {rental['area']}, {rental['district']}, {rental['state']}, {rental['pincode']}"

    expr_attr_vals = {
        ":bhk": int(rental["beds"]),
        ":rpm": int(rental["rpm"]),
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
        ":utilities": rental["utilities"],
        ":amenities": rental["amenities"],
        ":highlights": rental_info["highlights"],
        ":leaseTerms": rental_info["leaseTerms"],
        ":state": rental["state"],
        ":homeTour": rental_info["homeTour"],
        ":SearchItem": f"LISTING#{rental['state']}",
    }

    # Note: You have rentalInformation.highlights in the update expression, which is likely a typo.
    # It should probably be just :highlights. I've left it as is to match your original code.
    update_expr = (
        "SET bhk = :bhk, rpm = :rpm, occupantType = :occupantType, "
        "dateAvailable = :dateAvailable, district = :district, area = :area, "
        "rentalInformation.address = :full_address, rentalInformation.beds = :beds, "
        "rentalInformation.baths = :baths, rentalInformation.balcony = :balconies, "  # Corrected key
        "rentalInformation.facing = :facing, rentalInformation.floor = :floor, "
        "rentalInformation.maxOccupants = :maxOccupants, "
        "rentalInformation.waterAvailability = :waterAvailability, "
        "rentalInformation.hasElevator = :hasElevator, rentalInformation.hasBorewell = :hasBorewell, "
        "rentalInformation.utilities = :utilities, rentalInformation.amenities = :amenities, "
        "highlights = :highlights, leaseTerms = :leaseTerms, #state = :state, homeTour = :homeTour, SearchItem = :SearchItem"
    # Corrected `highlights` path
    )

    expr_attr_names = {
        "#state": "state"
    }

    return {
        "UpdateExpression": update_expr,
        "ExpressionAttributeValues": expr_attr_vals,
        "ExpressionAttributeNames": expr_attr_names
    }


def build_response(status_code, message, headers=None):
    response_body = message
    if not isinstance(message, str):
        response_body = json.dumps(message, cls=DecimalEncoder)

    return {
        "statusCode": status_code,
        "headers": headers or {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
        "body": response_body
    }


def validate_listing_info(listing):
    error = False
    required_fields = ["rentalInformation", "highlights", "leaseTerms"]
    for field in required_fields:
        if field not in listing:
            raise ValueError(f"Missing required field: {field}")
    else:
        if not 0 < (int(listing['rentalInformation']['beds'])) <= 5:
            error = True
        if not 1000 <= (int(listing['rentalInformation']['rpm'])) <= 50000:
            error = True
        if not 0 < (int(listing['rentalInformation']['baths'])) <= 5:
            error = True
        if not 0 <= (int(listing['rentalInformation']['balconies'])) <= 3:
            error = True
        if not (int(listing['rentalInformation']['floor'])) >= 0:
            error = True
        if not 1 <= (int(listing['rentalInformation']['maxOccupants'])) <= 10:
            error = True
        if not 1000 <= (int(listing['leaseTerms']['advanceAmount'])):
            error = True
        print('vacancy notification', int(listing['leaseTerms']['vacancyNotification']))
        if not 15 <= (int(listing['leaseTerms']['vacancyNotification'])) <= 365:
            error = True
        if not 1 <= (int(listing['leaseTerms']['leaseTenure'])) <= 36:
            error = True
        if not (int(listing['leaseTerms']['waterbill'])) <= 5000:
            error = True

        # get today date
        today_date = datetime.now().date()
        print('today date', today_date)
        date = datetime.strptime(listing['rentalInformation']['dateAvailable'], '%Y-%m-%d').date()
        if date <= today_date:
            error = True

    if error:
        raise MalformedValuesException()
    return True


class MalformedValuesException(Exception):
    def __init__(self, message="One or more values are malformed in the input"):
        self.message = message
        super().__init__(self.message)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


