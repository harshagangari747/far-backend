#!/usr/bin/env sh

aws dynamodb create-table \
  --table-name 'far-database' \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=userId,AttributeType=S \
    AttributeName=emailId,AttributeType=S \
    AttributeName=listingId,AttributeType=S \
    AttributeName=ownerId,AttributeType=S \
    AttributeName=SearchItem,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes "$(cat <<EOF
[
  {
    "IndexName": "GSI_UserByUserId",
    "KeySchema": [
      { "AttributeName": "userId", "KeyType": "HASH" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_UserByEmailId",
    "KeySchema": [
      { "AttributeName": "emailId", "KeyType": "HASH" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_TenantInterests",
    "KeySchema": [
      { "AttributeName": "PK", "KeyType": "HASH" },
      { "AttributeName": "SK", "KeyType": "RANGE" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_ListingsByOwner",
    "KeySchema": [
      { "AttributeName": "ownerId", "KeyType": "HASH" },
      { "AttributeName": "listingId", "KeyType": "RANGE" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_OwnerViewInterests",
    "KeySchema": [
      { "AttributeName": "PK", "KeyType": "HASH" },
      { "AttributeName": "SK", "KeyType": "RANGE" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_SearchByState",
    "KeySchema": [
      { "AttributeName": "SearchItem", "KeyType": "HASH" },
      { "AttributeName": "listingId", "KeyType": "RANGE" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  },
  {
    "IndexName": "GSI_GetListingsById",
    "KeySchema": [
      { "AttributeName": "PK", "KeyType": "HASH" }
    ],
    "Projection": { "ProjectionType": "ALL" }
  }


]
EOF
)" \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Project,Value=FindAroof \
  --table-class STANDARD \
  --region ap-south-1 \
  --profile far-developer \
  --output json
