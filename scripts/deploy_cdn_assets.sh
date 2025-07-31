#!/bin/bash
# Deploy CDN Assets Script
# Builds frontend and uploads assets to S3 for CDN delivery

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CDN_BUCKET=${CDN_S3_BUCKET:-"lafactoria-static-assets"}
AWS_REGION=${CDN_AWS_REGION:-"us-east-1"}
FRONTEND_DIR="frontend"
DIST_DIR="$FRONTEND_DIR/dist"

echo -e "${BLUE}=== CDN Asset Deployment ===${NC}"

# 1. Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm not found. Please install Node.js first.${NC}"
    exit 1
fi

# 2. Build frontend with CDN enabled
echo -e "\n${YELLOW}Building frontend assets...${NC}"
cd $FRONTEND_DIR

# Set CDN environment variables for build
export VITE_CDN_ENABLED=true
export VITE_CDN_URL=https://cdn.lafactoria.app
export VITE_STATIC_URL=https://static.lafactoria.app

# Clean and build
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}Build failed - dist directory not found${NC}"
    exit 1
fi

cd ..

# 3. Upload assets to S3
echo -e "\n${YELLOW}Uploading assets to S3...${NC}"

# Upload JS files with immutable cache
echo "Uploading JavaScript files..."
aws s3 sync $DIST_DIR/assets/js s3://$CDN_BUCKET/assets/js \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --content-type "application/javascript" \
    --metadata-directive REPLACE \
    --region $AWS_REGION

# Upload CSS files with immutable cache
echo "Uploading CSS files..."
aws s3 sync $DIST_DIR/assets/css s3://$CDN_BUCKET/assets/css \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --content-type "text/css" \
    --metadata-directive REPLACE \
    --region $AWS_REGION

# Upload images with immutable cache
echo "Uploading image files..."
aws s3 sync $DIST_DIR/assets/images s3://$CDN_BUCKET/assets/images \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --metadata-directive REPLACE \
    --region $AWS_REGION

# Upload fonts with immutable cache
echo "Uploading font files..."
aws s3 sync $DIST_DIR/assets/fonts s3://$CDN_BUCKET/assets/fonts \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --metadata-directive REPLACE \
    --region $AWS_REGION

# Upload index.html with no-cache
echo "Uploading HTML files..."
aws s3 cp $DIST_DIR/index.html s3://$CDN_BUCKET/index.html \
    --cache-control "no-cache, no-store, must-revalidate" \
    --content-type "text/html" \
    --metadata-directive REPLACE \
    --region $AWS_REGION

# 4. Warm CDN cache for critical assets
echo -e "\n${YELLOW}Warming CDN cache...${NC}"

# List of critical assets to pre-warm
CRITICAL_ASSETS=(
    "https://cdn.lafactoria.app/assets/js/vendor.js"
    "https://cdn.lafactoria.app/assets/js/index.js"
    "https://cdn.lafactoria.app/assets/css/index.css"
    "https://cdn.lafactoria.app/assets/fonts/inter.woff2"
)

for asset in "${CRITICAL_ASSETS[@]}"; do
    echo "Warming: $asset"
    curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" "$asset"
done

# 5. Invalidate Cloudflare cache (optional)
if [ "$INVALIDATE_CACHE" = "true" ] && [ -n "$CLOUDFLARE_API_TOKEN" ] && [ -n "$CLOUDFLARE_ZONE_ID" ]; then
    echo -e "\n${YELLOW}Invalidating Cloudflare cache...${NC}"
    
    curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/purge_cache" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data '{"purge_everything":false,"files":["https://cdn.lafactoria.app/index.html"]}' \
        -s -o /dev/null
    
    echo "Cache invalidated for index.html"
fi

# 6. Validate CDN deployment
echo -e "\n${YELLOW}Validating CDN deployment...${NC}"
python3 scripts/validate_cdn_simple.py

echo -e "\n${GREEN}✓ CDN assets deployed successfully!${NC}"
echo -e "${BLUE}CDN URL: https://cdn.lafactoria.app${NC}"
echo -e "${BLUE}Static URL: https://static.lafactoria.app${NC}"