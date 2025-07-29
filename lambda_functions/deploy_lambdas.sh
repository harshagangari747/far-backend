#!/usr/bin/env sh

#create search lambda function
aws lambda create-function \
  --function-name search \
  --runtime python3.12 \
  --handler search_handler.handler \
  --zip-file fileb://search.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer

#create profile lambda function
aws lambda create-function \
  --function-name profile \
  --runtime python3.12 \
  --handler profile_handler.handler \
  --zip-file fileb://profile.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer

#create listings (listings_handler) lambda function
aws lambda create-function \
  --function-name update_listings \
  --runtime python3.12 \
  --handler listings_handler.handler \
  --zip-file fileb://update_listings.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer

#create listings (delete_handler) lambda function
aws lambda create-function \
  --function-name delete_listing \
  --runtime python3.12 \
  --handler delete_listing_handler.handler \
  --zip-file fileb://delete_listing.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer

#create listings (owner_listing_handler) lambda function
aws lambda create-function \
  --function-name owner_listing \
  --runtime python3.12 \
  --handler owner_listing_handler.handler \
  --zip-file fileb://owner_listing.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer

#create interests lambda function
aws lambda create-function \
  --function-name interests \
  --runtime python3.12 \
  --handler interests_handler.handler \
  --zip-file fileb://interests.zip \
  --region ap-south-1 \
  --role arn:aws:iam::777967551979:role/Lambda-DynamoDb-Access-Role \
  --profile far-developer