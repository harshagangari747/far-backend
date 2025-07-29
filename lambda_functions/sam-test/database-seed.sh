#!/usr/bin/env sh

# DynamoDB Seed Script for far-database-local-setup
# This script populates the database with users, listings, interests, and matches

ENDPOINT_URL="http://localhost:8000"
REGION="ap-south-1"
TABLE_NAME="far-database-local-setup"

echo "Starting database seeding..."

# ========== USERS ==========
echo "Creating users..."

# User 1: Maro
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "user#maro-001"},
    "SK": {"S": "user#maro@findaroof.com"},
    "userId": {"S": "maro-001"},
    "emailId": {"S": "maro@findaroof.com"},
    "itemType": {"S": "userInfo"},
    "name": {"S": "Maro Johnson"},
    "contactnum": {"S": "+91-9876543210"},
    "gender": {"S": "Male"},
    "age": {"N": "28"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# User 2: Ferb
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "user#ferb-002"},
    "SK": {"S": "user#ferb@findaroof.com"},
    "userId": {"S": "ferb-002"},
    "emailId": {"S": "ferb@findaroof.com"},
    "itemType": {"S": "userInfo"},
    "name": {"S": "Ferb Fletcher"},
    "contactnum": {"S": "+91-9876543211"},
    "gender": {"S": "Male"},
    "age": {"N": "32"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# User 3: Rancho
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "user#rancho-003"},
    "SK": {"S": "user#rancho@findaroof.com"},
    "userId": {"S": "rancho-003"},
    "emailId": {"S": "rancho@findaroof.com"},
    "itemType": {"S": "userInfo"},
    "name": {"S": "Rancho Chanchad"},
    "contactnum": {"S": "+91-9876543212"},
    "gender": {"S": "Male"},
    "age": {"N": "26"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# User 4: Zeus
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "user#zeus-004"},
    "SK": {"S": "user#zeus@findaroof.com"},
    "userId": {"S": "zeus-004"},
    "emailId": {"S": "zeus@findaroof.com"},
    "itemType": {"S": "userInfo"},
    "name": {"S": "Zeus Thunder"},
    "contactnum": {"S": "+91-9876543213"},
    "gender": {"S": "Male"},
    "age": {"N": "35"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# ========== LISTINGS ==========
echo "Creating listings..."

# Maro's Listings (3 listings)
# Maro Listing 1
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#maro-listing-001"},
    "SK": {"S": "LISTING#maro-001"},
    "listingId": {"S": "maro-listing-001"},
    "ownerId": {"S": "maro-001"},
    "SearchItem": {"S": "LISTING#Karnataka"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "2"},
    "rpm": {"N": "25000"},
    "occupantType": {"S": "family"},
    "dateAvailable": {"S": "2025-07-15"},
    "state": {"S": "Karnataka"},
    "district": {"S": "Bangalore Urban"},
    "area": {"N": "1200.5"},
    "rentalInformation": {
      "M": {
        "address": {"S": "123 MG Road, Bangalore, Karnataka 560001"},
        "beds": {"N": "2"},
        "baths": {"N": "2"},
        "balcony": {"N": "1"},
        "facing": {"S": "east"},
        "utilities": {"L": [{"S": "WiFi"}, {"S": "Cable TV"}, {"S": "Gas Connection"}]},
        "amenities": {"L": [{"S": "Gym"}, {"S": "Swimming Pool"}, {"S": "Parking"}]},
        "maxOccupants": {"N": "4"},
        "floor": {"N": "5"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": true},
        "hasBorewell": {"BOOL": true}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/maro-listing-001"},
    "highLights": {"L": [{"S": "Near Metro Station"}, {"S": "Fully Furnished"}, {"S": "24/7 Security"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "50000"},
        "notifyBeforeVacancy": {"S": "30 days"},
        "leaseTenure": {"N": "12"},
        "electricityBill": {"S": "tenant"},
        "waterBill": {"N": "500"},
        "maintainance": {"N": "2000"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Maro Listing 2
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#maro-listing-002"},
    "SK": {"S": "LISTING#maro-001"},
    "listingId": {"S": "maro-listing-002"},
    "ownerId": {"S": "maro-001"},
    "SearchItem": {"S": "LISTING#Karnataka"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "3"},
    "rpm": {"N": "35000"},
    "occupantType": {"S": "bachelor"},
    "dateAvailable": {"S": "2025-08-01"},
    "state": {"S": "Karnataka"},
    "district": {"S": "Bangalore Urban"},
    "area": {"N": "1500.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "456 Koramangala, Bangalore, Karnataka 560034"},
        "beds": {"N": "3"},
        "baths": {"N": "2.5"},
        "balcony": {"N": "2"},
        "facing": {"S": "north"},
        "utilities": {"L": [{"S": "WiFi"}, {"S": "DTH"}, {"S": "Gas Pipeline"}]},
        "amenities": {"L": [{"S": "Clubhouse"}, {"S": "Garden"}, {"S": "Power Backup"}]},
        "maxOccupants": {"N": "6"},
        "floor": {"N": "3"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": true},
        "hasBorewell": {"BOOL": false}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/maro-listing-002"},
    "highLights": {"L": [{"S": "IT Hub Proximity"}, {"S": "Semi-Furnished"}, {"S": "Spacious Rooms"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "70000"},
        "notifyBeforeVacancy": {"S": "45 days"},
        "leaseTenure": {"N": "11"},
        "electricityBill": {"S": "shared"},
        "waterBill": {"N": "800"},
        "maintainance": {"N": "3000"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Maro Listing 3
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#maro-listing-003"},
    "SK": {"S": "LISTING#maro-001"},
    "listingId": {"S": "maro-listing-003"},
    "ownerId": {"S": "maro-001"},
    "SearchItem": {"S": "LISTING#Tamil Nadu"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "1"},
    "rpm": {"N": "18000"},
    "occupantType": {"S": "family"},
    "dateAvailable": {"S": "2025-07-30"},
    "state": {"S": "Tamil Nadu"},
    "district": {"S": "Chennai"},
    "area": {"N": "800.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "789 T Nagar, Chennai, Tamil Nadu 600017"},
        "beds": {"N": "1"},
        "baths": {"N": "1"},
        "balcony": {"N": "1"},
        "facing": {"S": "south"},
        "utilities": {"L": [{"S": "WiFi"}, {"S": "Cable TV"}]},
        "amenities": {"L": [{"S": "Parking"}, {"S": "Security"}]},
        "maxOccupants": {"N": "2"},
        "floor": {"N": "2"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": false},
        "hasBorewell": {"BOOL": true}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/maro-listing-003"},
    "highLights": {"L": [{"S": "Shopping District"}, {"S": "Budget Friendly"}, {"S": "Well Connected"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "36000"},
        "notifyBeforeVacancy": {"S": "30 days"},
        "leaseTenure": {"N": "12"},
        "electricityBill": {"S": "owner"},
        "waterBill": {"N": "300"},
        "maintainance": {"N": "1000"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Ferb's Listings (3 listings)
# Ferb Listing 1
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#ferb-listing-001"},
    "SK": {"S": "LISTING#ferb-002"},
    "listingId": {"S": "ferb-listing-001"},
    "ownerId": {"S": "ferb-002"},
    "SearchItem": {"S": "LISTING#Maharashtra"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "2"},
    "rpm": {"N": "45000"},
    "occupantType": {"S": "family"},
    "dateAvailable": {"S": "2025-08-15"},
    "state": {"S": "Maharashtra"},
    "district": {"S": "Mumbai"},
    "area": {"N": "900.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "321 Bandra West, Mumbai, Maharashtra 400050"},
        "beds": {"N": "2"},
        "baths": {"N": "2"},
        "balcony": {"N": "1"},
        "facing": {"S": "west"},
        "utilities": {"L": [{"S": "High Speed WiFi"}, {"S": "DTH"}, {"S": "Gas Pipeline"}]},
        "amenities": {"L": [{"S": "Sea View"}, {"S": "Gym"}, {"S": "Swimming Pool"}, {"S": "Concierge"}]},
        "maxOccupants": {"N": "4"},
        "floor": {"N": "12"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": true},
        "hasBorewell": {"BOOL": false}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/ferb-listing-001"},
    "highLights": {"L": [{"S": "Sea Facing"}, {"S": "Luxury Building"}, {"S": "Prime Location"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "135000"},
        "notifyBeforeVacancy": {"S": "60 days"},
        "leaseTenure": {"N": "12"},
        "electricityBill": {"S": "tenant"},
        "waterBill": {"N": "1200"},
        "maintainance": {"N": "5000"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Ferb Listing 2
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#ferb-listing-002"},
    "SK": {"S": "LISTING#ferb-002"},
    "listingId": {"S": "ferb-listing-002"},
    "ownerId": {"S": "ferb-002"},
    "SearchItem": {"S": "LISTING#Maharashtra"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "3"},
    "rpm": {"N": "65000"},
    "occupantType": {"S": "bachelor"},
    "dateAvailable": {"S": "2025-09-01"},
    "state": {"S": "Maharashtra"},
    "district": {"S": "Mumbai"},
    "area": {"N": "1300.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "654 Powai, Mumbai, Maharashtra 400076"},
        "beds": {"N": "3"},
        "baths": {"N": "3"},
        "balcony": {"N": "2"},
        "facing": {"S": "northeast"},
        "utilities": {"L": [{"S": "Fiber Internet"}, {"S": "Smart TV"}, {"S": "Modular Kitchen"}]},
        "amenities": {"L": [{"S": "Lake View"}, {"S": "Jogging Track"}, {"S": "Business Center"}, {"S": "Rooftop Garden"}]},
        "maxOccupants": {"N": "6"},
        "floor": {"N": "8"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": true},
        "hasBorewell": {"BOOL": true}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/ferb-listing-002"},
    "highLights": {"L": [{"S": "Lake Facing"}, {"S": "IT Professionals Preferred"}, {"S": "Modern Amenities"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "130000"},
        "notifyBeforeVacancy": {"S": "45 days"},
        "leaseTenure": {"N": "11"},
        "electricityBill": {"S": "shared"},
        "waterBill": {"N": "1000"},
        "maintainance": {"N": "4500"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Ferb Listing 3
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#ferb-listing-003"},
    "SK": {"S": "LISTING#ferb-002"},
    "listingId": {"S": "ferb-listing-003"},
    "ownerId": {"S": "ferb-002"},
    "SearchItem": {"S": "LISTING#Maharashtra"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "1"},
    "rpm": {"N": "32000"},
    "occupantType": {"S": "family"},
    "dateAvailable": {"S": "2025-07-20"},
    "state": {"S": "Maharashtra"},
    "district": {"S": "Pune"},
    "area": {"N": "650.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "987 Hinjewadi, Pune, Maharashtra 411057"},
        "beds": {"N": "1"},
        "baths": {"N": "1"},
        "balcony": {"N": "1"},
        "facing": {"S": "east"},
        "utilities": {"L": [{"S": "WiFi Ready"}, {"S": "Gas Connection"}]},
        "amenities": {"L": [{"S": "IT Park Proximity"}, {"S": "Food Court"}, {"S": "ATM"}]},
        "maxOccupants": {"N": "3"},
        "floor": {"N": "4"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": true},
        "hasBorewell": {"BOOL": true}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/ferb-listing-003"},
    "highLights": {"L": [{"S": "IT Hub Location"}, {"S": "Ready to Move"}, {"S": "Young Professionals"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "64000"},
        "notifyBeforeVacancy": {"S": "30 days"},
        "leaseTenure": {"N": "12"},
        "electricityBill": {"S": "tenant"},
        "waterBill": {"N": "400"},
        "maintainance": {"N": "2200"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Rancho's Listing (1 listing)
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "LISTING#rancho-listing-001"},
    "SK": {"S": "LISTING#rancho-003"},
    "listingId": {"S": "rancho-listing-001"},
    "ownerId": {"S": "rancho-003"},
    "SearchItem": {"S": "LISTING#Rajasthan"},
    "itemType": {"S": "listing"},
    "bhk": {"N": "4"},
    "rpm": {"N": "40000"},
    "occupantType": {"S": "family"},
    "dateAvailable": {"S": "2025-08-10"},
    "state": {"S": "Rajasthan"},
    "district": {"S": "Jaipur"},
    "area": {"N": "2200.0"},
    "rentalInformation": {
      "M": {
        "address": {"S": "111 Vaishali Nagar, Jaipur, Rajasthan 302021"},
        "beds": {"N": "4"},
        "baths": {"N": "3"},
        "balcony": {"N": "3"},
        "facing": {"S": "north"},
        "utilities": {"L": [{"S": "WiFi"}, {"S": "Dish TV"}, {"S": "Gas Pipeline"}, {"S": "Inverter"}]},
        "amenities": {"L": [{"S": "Garden"}, {"S": "Parking for 2 Cars"}, {"S": "Servant Quarter"}, {"S": "Temple"}]},
        "maxOccupants": {"N": "8"},
        "floor": {"N": "1"},
        "waterAvailability": {"S": "daily"},
        "hasElevator": {"BOOL": false},
        "hasBorewell": {"BOOL": true}
      }
    },
    "homeTour": {"S": "https://virtualtour.com/rancho-listing-001"},
    "highLights": {"L": [{"S": "Independent House"}, {"S": "Spacious"}, {"S": "Family Friendly"}, {"S": "Traditional Architecture"}]},
    "leaseTerms": {
      "M": {
        "advance": {"N": "80000"},
        "notifyBeforeVacancy": {"S": "60 days"},
        "leaseTenure": {"N": "24"},
        "electricityBill": {"S": "tenant"},
        "waterBill": {"N": "600"},
        "maintainance": {"N": "3500"}
      }
    }
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# ========== INTERESTS ==========
echo "Creating interests..."

# Maro's interests (1 Ferb listing + 1 Rancho listing)
# Maro interested in Ferb listing 1
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#maro-001"},
    "SK": {"S": "INTERESTS#ferb-listing-001"},
    "tenantId": {"S": "maro-001"},
    "listingId": {"S": "ferb-listing-001"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Maro interested in Rancho listing 1
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#maro-001"},
    "SK": {"S": "INTERESTS#rancho-listing-001"},
    "tenantId": {"S": "maro-001"},
    "listingId": {"S": "rancho-listing-001"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Rancho's interests (2 Ferb listings that Maro also showed interest in)
# Rancho interested in Ferb listing 1 (common with Maro)
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#rancho-003"},
    "SK": {"S": "INTERESTS#ferb-listing-001"},
    "tenantId": {"S": "rancho-003"},
    "listingId": {"S": "ferb-listing-001"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Rancho interested in Ferb listing 2 (we'll assume Maro also showed interest in this one)
# First, add Maro's interest in Ferb listing 2
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#maro-001"},
    "SK": {"S": "INTERESTS#ferb-listing-002"},
    "tenantId": {"S": "maro-001"},
    "listingId": {"S": "ferb-listing-002"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Then Rancho's interest in Ferb listing 2
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#rancho-003"},
    "SK": {"S": "INTERESTS#ferb-listing-002"},
    "tenantId": {"S": "rancho-003"},
    "listingId": {"S": "ferb-listing-002"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Zeus's interests (2 Ferb listings)
# Zeus interested in Ferb listing 2
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#zeus-004"},
    "SK": {"S": "INTERESTS#ferb-listing-002"},
    "tenantId": {"S": "zeus-004"},
    "listingId": {"S": "ferb-listing-002"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Zeus interested in Ferb listing 3
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "INTERESTS#zeus-004"},
    "SK": {"S": "INTERESTS#ferb-listing-003"},
    "tenantId": {"S": "zeus-004"},
    "listingId": {"S": "ferb-listing-003"},
    "itemType": {"S": "interest"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# ========== MATCHES ==========
echo "Creating matches..."

# Matches for Ferb's listings
# Match 1: Ferb listing 1 - Maro showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-001"},
    "SK": {"S": "MATCHES#maro-001"},
    "listingId": {"S": "ferb-listing-001"},
    "tenantId": {"S": "maro-001"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Match 2: Ferb listing 1 - Rancho showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-001"},
    "SK": {"S": "MATCHES#rancho-003"},
    "listingId": {"S": "ferb-listing-001"},
    "tenantId": {"S": "rancho-003"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Match 3: Ferb listing 2 - Maro showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-002"},
    "SK": {"S": "MATCHES#maro-001"},
    "listingId": {"S": "ferb-listing-002"},
    "tenantId": {"S": "maro-001"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Match 4: Ferb listing 2 - Rancho showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-002"},
    "SK": {"S": "MATCHES#rancho-003"},
    "listingId": {"S": "ferb-listing-002"},
    "tenantId": {"S": "rancho-003"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Match 5: Ferb listing 2 - Zeus showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-002"},
    "SK": {"S": "MATCHES#zeus-004"},
    "listingId": {"S": "ferb-listing-002"},
    "tenantId": {"S": "zeus-004"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Match 6: Ferb listing 3 - Zeus showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#ferb-listing-003"},
    "SK": {"S": "MATCHES#zeus-004"},
    "listingId": {"S": "ferb-listing-003"},
    "tenantId": {"S": "zeus-004"},
    "ownerId": {"S": "ferb-002"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION 

# Matches for Rancho's listing
# Match 7: Rancho listing 1 - Maro showed interest
aws dynamodb put-item \
  --table-name $TABLE_NAME \
  --item '{
    "PK": {"S": "MATCHES#rancho-listing-001"},
    "SK": {"S": "MATCHES#maro-001"},
    "listingId": {"S": "rancho-listing-001"},
    "tenantId": {"S": "maro-001"},
    "ownerId": {"S": "rancho-003"},
    "itemType": {"S": "match"}
  }' \
  --endpoint-url $ENDPOINT_URL \
  --region $REGION \
  --output json

# Note: No matches for Maro's listings as per the requirements (no one showed interest in Maro's listings)

echo "Database seeding completed successfully!"
echo ""
echo "Summary:"
echo "- 4 Users created: Maro, Ferb, Rancho, Zeus"
echo "- 7 Listings created: 3 by Maro, 3 by Ferb, 1 by Rancho"
echo "- 6 Interest records created"
echo "- 7 Match records created"
echo ""
echo "You can now query the database to verify the data:"
echo "aws dynamodb scan --table-name $TABLE_NAME --endpoint-url $ENDPOINT_URL --region $ REGIONs"