#!/usr/bin/env sh
export default_region='ap-south-1'
export default_profile='far-developer'

#S3 variables
export default_bucket_name='far-app-storage'
export acl_value='private'

#api gateway variables
export api_gw_name="far-api-gateway"
export api_gw_stage_name="prod"
export api_gw_description="API Gateway to handle requests to FAR website in the backend"
export api_gw_lambda_integration_type="AWS_PROXY"

#Amazon Cognito User Pool variables
export cognito_user_pool_name="far_user_pool"
export cognito_user_pool_app_client="far-app-client"

#Amazon DynamoDb Table varialbes
export dynamodb_table_name="far-database"




# Create S3 bucket
s3output=$(aws s3api create-bucket \
--acl $acl_value \
--bucket $default_bucket_name \
--region $default_region \
--create-bucket-configuration LocationConstraint=$default_region \
--profile $default_profile 2>&1)

exit_code=$?

if [ $exit_code -ne 0 ]; then
  echo "Step1: Bucket \"$default_bucket_name\" creation failed. It might happened because bucket already exists. Debug for more information"
else
  echo "Step1: Bucket $default_bucket_name created successfully"
  echo "$cli_output"
fi

# Create api gateway

API_ID=$(aws apigateway get-rest-apis \
  --region "$default_region" \
  --profile "$default_profile" \
  --query "items[?name=='$api_gw_name'].id" \
  --output text)

if [ -z "$API_ID" ]; then
  echo "API Gateway '$api_gw_name' does not exist. Creating it..."
  cli_output=$(aws apigateway create-rest-api \
--name $api_gw_name \
--description "$api_gw_description" \
--region $default_region \
--profile $default_profile 2>&1)

  exit_code=$?

  if [ $exit_code -ne 0 ]; then
    echo "Step2: Api Gateway \"$api_gw_name\" creation failed. Debug for more information"
  else
    echo "Step2: Api Gateway $api_gw_name created successfully"
    echo "$cli_output"
  fi
else
  echo "Step2: Api Gateway \"$api_gw_name\" already exists. Retrieving essential information... "
  far_api_gw_id=$(aws apigateway get-rest-apis \
 --region $default_region \
 --profile $default_profile \
 --query "items[?name=='$api_gw_name'].id | [0]" \
 --output text)
 echo "$api_gw_name id: $far_api_gw_id"

 far_api_gw_root_resource_id=$(aws apigateway get-rest-apis \
 --region $default_region \
 --profile $default_profile \
 --query "items[?name=='$api_gw_name'].rootResourceId | [0]" \
 --output text)
 echo "$api_gw_name root resource id: $far_api_gw_root_resource_id"
fi




# Create resources in the api gateway
# === RESOURCE PATHS (flat structure) ===
resources=(
  "search"
  "listings"
  "interests"
  "auth"
  "profile"
)

echo "Creating resources in the API $api_gw_name"

for path in "${resources[@]}"; do
  # Check if resource already exists under the root
  existing_resource_id=$(aws apigateway get-resources \
    --rest-api-id "$far_api_gw_id" \
    --region "$default_region" \
    --profile "$default_profile" \
    --query "items[?path=='/${path}'].id | [0]" \
    --output text)

  if [ "$existing_resource_id" != "None" ] && [ -n "$existing_resource_id" ]; then
    echo "Resource /$path already exists with ID: $existing_resource_id, skipping creation."
  else
    echo "Creating resource /$path"
    aws apigateway create-resource \
      --rest-api-id "$far_api_gw_id" \
      --region "$default_region" \
      --parent-id "$far_api_gw_root_resource_id" \
      --path-part "$path" \
      --profile "$default_profile"
  fi
done

echo "Resource creation check completed."

# Create dynamodb table

echo "Creating $dynamodb_table_name dynamodb table..."
aws dynamodb create-table \
  --table-name $dynamodb_table_name \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=userId,AttributeType=S \
    AttributeName=emailId,AttributeType=S \
    AttributeName=tenantId,AttributeType=S \
    AttributeName=listingId,AttributeType=S \
    AttributeName=ownerId,AttributeType=S \
    AttributeName=SearchItem,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes '[
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
        { "AttributeName": "tenantId", "KeyType": "HASH" },
        { "AttributeName": "listingId", "KeyType": "RANGE" }
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
        { "AttributeName": "listingId", "KeyType": "HASH" },
        { "AttributeName": "tenantId", "KeyType": "RANGE" }
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
    }
  ]' \
--billing-mode PAY_PER_REQUEST \
--tags Key=Project,Value=FindAroof \
--table-class STANDARD \
--profile $default_profile







