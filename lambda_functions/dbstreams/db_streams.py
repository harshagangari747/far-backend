import json
import boto3
import os
import smtplib
from boto3.dynamodb.conditions import Key, Attr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta, datetime, timezone

DEFAULT_REGION = os.environ['DEFAULT_REGION']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

dynamdodb = boto3.resource('dynamodb', region_name=DEFAULT_REGION)
table = dynamdodb.Table(DYNAMODB_TABLE_NAME)

from_email_address = os.environ['FROM_EMAIL_ADDRESS']
app_password = os.environ['EMAIL_APP_PASSWORD']

login_link = os.environ['LOGIN_LINK']


def lambda_handler(event, context):
    # TODO implement
    print('dynamdodb streams', event)
    try:
        print('dynamdodb streams', event['Records'][0]['eventName'])
        records = event['Records']
        for record in records:
            event_name = record['eventName']
            approx_inserted_time = record['dynamodb']['ApproximateCreationDateTime']
            approx_inserted_time = datetime.fromtimestamp(approx_inserted_time, tz=timezone.utc)
            current_time = datetime.now(tz=timezone.utc)
            print('approx_inserted_time', approx_inserted_time)
            print('current_time', current_time)
            if current_time - approx_inserted_time > timedelta(seconds=4):
                print('event is older than 4 seconds, skipping')
                continue
            if event_name == 'INSERT':
                print('item inserted', record['dynamodb']['NewImage'])

                pk = record['dynamodb']['Keys']['PK']['S']
                if pk.startswith('MATCHES#'):
                    owner_id = record['dynamodb']['NewImage']['ownerId']['S']
                    listing_id = record['dynamodb']['NewImage']['listingId']['S']
                    owner_email = get_user_email_by_user_id(owner_id)
                    print('owner_email', owner_email)

                    # send email to owner
                    send_email(owner_email, listing_id, True)
                    print(' interest notification email sent to owner', owner_email)

            elif event_name == 'REMOVE':
                print('handling remove of listings')
                pk = record['dynamodb']['Keys']['PK']['S']
                sk = record['dynamodb']['Keys']['SK']['S']
                print('pk', pk)
                print('sk', sk)
                if sk.startswith('LISTING#') and pk.startswith('LISTING#'):
                    user_id = sk.split('#')[1]
                    listing_id = pk.split('#')[1]
                    print('user id', user_id)
                    owner_email = get_user_email_by_user_id(user_id)

                    print('fetched owner_email to send remove updates', owner_email)
                    send_email(owner_email, listing_id, False)

    except Exception as ex:
        print('error', ex)


def get_user_email_by_user_id(user_id):
    if not user_id:
        raise UserNotFoundException
    KeyConditionExpression = Key('PK').eq(f"user#{user_id}")
    result = table.query(KeyConditionExpression=KeyConditionExpression)
    if not result['Items']:
        raise UserNotFoundException
    print('result', result)
    return result['Items'][0]['emailId']


def send_email(receipient_email, listing_id, isInterest):
    sender_email = from_email_address
    print('sending email to', receipient_email)
    receiver_email = receipient_email
    password = app_password

    if isInterest:
        subject = "Your Listing Found A Match!"
        body = (
            f"Thank you for using <b>FarApp</b>."
            f"We're excited to inform you that your listing with id <b>{listing_id}</b> has been matched with an interest."
            f"Please log in to your account to view the details.</p><a href='{login_link}'>Login to your FAR account</a></p>")
    else:
        subject = "Alert! Listing Deleted!"
        body = (
            f"We have noticed that your listing with id <b>{listing_id}</b> has been deleted."
            f"If you have not done this operation contact the admin team as soon as possible."
            f"<p><a href='{login_link}'>Login to your FAR account</a></p>")

    # Compose the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    html_content = f"""
    <html>
    <body>
    <p>Hi there!</p>
    <p>{body}</p>
    <p>Best regards,<br>FarApp Team</p>
    </body>
    </html>"""

    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return {"statusCode": 200, "body": "Email sent successfully!"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


