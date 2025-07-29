#!/usr/bin/env sh

set -e

REGION="ap-south-1"
PROFILE="far-developer"
ACCOUNT_ID="777967551979"
API_NAME="far-api-gateway"
STAGE_NAME="prod"

# Format: "<path> <method> <lambda_name>"
ENDPOINTS=(
  "/search GET search"
  "/listings POST update_listings"
  "/listings PUT update_listings"
  "/listings DELETE delete_listing"
  "/listings/owner GET owner_listing"
  "/interests POST interests"
  "/interests GET interests"
  "/profile GET profile"
  "/profile POST profile"
  "/profile PATCH profile"
)

# Get API Gateway ID
API_ID=$(aws apigateway get-rest-apis --region "$REGION" --profile "$PROFILE" \
  --query "items[?name=='$API_NAME'].id" --output text)

if [ -z "$API_ID" ]; then
  echo "API Gateway '$API_NAME' not found."
  exit 1
fi

echo "API Gateway ID: $API_ID"

# Get all existing resources
RESOURCE_DATA=$(aws apigateway get-resources \
  --rest-api-id "$API_ID" \
  --region "$REGION" --profile "$PROFILE")

for entry in "${ENDPOINTS[@]}"; do
  IFS=' ' read -r PATH METHOD LAMBDA_NAME <<< "$entry"

  RESOURCE_ID=$(echo "$RESOURCE_DATA" | /opt/anaconda3/bin/jq -r --arg path "$PATH" '.items[] | select(.path == $path) | .id')

  if [ -z "$RESOURCE_ID" ]; then
    echo "Resource '$PATH' not found in API Gateway. Skipping."
    continue
  fi

  echo "Attaching method $METHOD on path $PATH to Lambda function $LAMBDA_NAME"

  # Create or update method
  aws apigatewayv2 put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$RESOURCE_ID" \
    --http-method "$METHOD" \
    --authorization-type "NONE" \
    --region "$REGION" --profile "$PROFILE" || true

  # Configure Lambda proxy integration
  aws apigatewayv2 put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$RESOURCE_ID" \
    --http-method "$METHOD" \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_NAME/invocations" \
    --region "$REGION" --profile "$PROFILE"

  # Grant API Gateway permission to invoke the Lambda
  STATEMENT_ID="apigateway-${METHOD,,}-$(echo "$PATH" | tr -d '/')"

  aws lambda add-permission \
    --function-name "$LAMBDA_NAME" \
    --statement-id "$STATEMENT_ID" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/$METHOD$PATH" \
    --region "$REGION" --profile "$PROFILE" || true

  echo "Method $METHOD for path $PATH integrated with $LAMBDA_NAME"
done

# Deploy the changes to the stage
echo "Deploying to stage: $STAGE_NAME"
aws apigateway create-deployment \
  --rest-api-id "$API_ID" \
  --stage-name "$STAGE_NAME" \
  --region "$REGION" --profile "$PROFILE"

echo "Deployment complete. API Base URL:"
echo "https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE_NAME"
