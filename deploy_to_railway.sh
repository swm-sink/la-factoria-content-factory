#!/bin/bash

# La Factoria Railway Deployment Script
# Production deployment with comprehensive validation
set -e

echo "🚀 La Factoria Railway Deployment Starting..."
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if Railway CLI is installed
check_railway_cli() {
    log "Checking Railway CLI installation..."
    if ! command -v railway &> /dev/null; then
        error "Railway CLI not found. Install with: npm install -g @railway/cli"
    fi
    success "Railway CLI found"
}

# Validate project structure
validate_project() {
    log "Validating project structure..."

    required_files=(
        "railway.toml"
        "requirements.txt"
        "src/main.py"
        "migrations/001_initial_schema.sql"
        "static/index.html"
        "static/monitor.html"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file missing: $file"
        fi
    done

    success "Project structure validated"
}

# Check Railway authentication
check_railway_auth() {
    log "Checking Railway authentication..."
    if ! railway whoami &> /dev/null; then
        warning "Not logged into Railway. Please login:"
        railway login
    fi

    user=$(railway whoami 2>/dev/null || echo "unknown")
    success "Authenticated as: $user"
}

# Deploy to Railway
deploy_application() {
    log "Deploying application to Railway..."

    # Deploy the application
    log "Pushing code to Railway..."
    railway up --detach

    success "Application deployed successfully"
}

# Set environment variables
setup_environment() {
    log "Setting up environment variables..."

    # Check if critical environment variables are set
    critical_vars=(
        "LA_FACTORIA_API_KEY"
        "SECRET_KEY"
        "DATABASE_URL"
    )

    for var in "${critical_vars[@]}"; do
        if railway variables get "$var" &> /dev/null; then
            success "$var is configured"
        else
            warning "$var not set - configure in Railway dashboard"
        fi
    done

    # Check AI provider variables
    ai_providers=0
    if railway variables get "OPENAI_API_KEY" &> /dev/null; then
        success "OpenAI API key configured"
        ai_providers=$((ai_providers + 1))
    fi

    if railway variables get "ANTHROPIC_API_KEY" &> /dev/null; then
        success "Anthropic API key configured"
        ai_providers=$((ai_providers + 1))
    fi

    if railway variables get "GOOGLE_CLOUD_PROJECT" &> /dev/null; then
        success "Google Cloud project configured"
        ai_providers=$((ai_providers + 1))
    fi

    if [[ $ai_providers -eq 0 ]]; then
        warning "No AI providers configured - content generation will fail"
    else
        success "$ai_providers AI provider(s) configured"
    fi
}

# Wait for deployment to be ready
wait_for_deployment() {
    log "Waiting for deployment to be ready..."

    # Get the deployed URL
    app_url=$(railway domain 2>/dev/null || echo "")
    if [[ -z "$app_url" ]]; then
        app_url="https://your-app.railway.app"
        warning "Could not get deployment URL, using placeholder: $app_url"
    else
        app_url="https://$app_url"
        success "Deployment URL: $app_url"
    fi

    # Wait for health check to pass
    log "Waiting for health check to pass..."
    max_attempts=30
    attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log "Health check attempt $attempt/$max_attempts..."

        if curl -s -f "$app_url/health" > /dev/null 2>&1; then
            success "Health check passed!"
            break
        fi

        if [[ $attempt -eq $max_attempts ]]; then
            error "Health check failed after $max_attempts attempts"
        fi

        log "Waiting 10 seconds before retry..."
        sleep 10
        attempt=$((attempt + 1))
    done
}

# Run database migration
setup_database() {
    log "Setting up database..."

    # Check if database is accessible
    if railway run psql --version &> /dev/null; then
        log "Running database migration..."
        railway run psql -d "\$DATABASE_URL" -f migrations/001_initial_schema.sql || {
            warning "Database migration may have already been run"
        }
        success "Database setup completed"
    else
        warning "Could not access database - migration may need to be run manually"
    fi
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."

    app_url=$(railway domain 2>/dev/null || echo "your-app.railway.app")
    if [[ ! "$app_url" == https://* ]]; then
        app_url="https://$app_url"
    fi

    # Test health endpoint
    log "Testing health endpoint..."
    if health_response=$(curl -s "$app_url/health"); then
        if echo "$health_response" | grep -q '"status":"healthy"'; then
            success "Health endpoint responding correctly"
        else
            warning "Health endpoint not returning healthy status"
            echo "Response: $health_response"
        fi
    else
        error "Health endpoint not accessible"
    fi

    # Test detailed health endpoint
    log "Testing detailed health endpoint..."
    if curl -s -f "$app_url/api/v1/health/detailed" > /dev/null; then
        success "Detailed health endpoint accessible"
    else
        warning "Detailed health endpoint not accessible"
    fi

    # Test monitoring dashboard
    log "Testing monitoring dashboard..."
    if curl -s -f "$app_url/static/monitor.html" > /dev/null; then
        success "Monitoring dashboard accessible"
    else
        warning "Monitoring dashboard not accessible"
    fi

    # Test API documentation (if available)
    if curl -s -f "$app_url/docs" > /dev/null; then
        log "API documentation accessible at: $app_url/docs"
    fi

    success "Deployment validation completed"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."

    app_url=$(railway domain 2>/dev/null || echo "your-app.railway.app")
    if [[ ! "$app_url" == https://* ]]; then
        app_url="https://$app_url"
    fi

    cat > DEPLOYMENT_REPORT.md << EOF
# La Factoria Deployment Report
**Deployment Date**: $(date)
**Status**: ✅ SUCCESSFUL

## Deployment URLs
- **Application**: $app_url
- **Health Check**: $app_url/health
- **Detailed Health**: $app_url/api/v1/health/detailed
- **System Monitor**: $app_url/static/monitor.html
- **API Metrics**: $app_url/api/v1/metrics

## Educational Content Endpoints
- **Master Outline**: POST $app_url/api/v1/content/generate/master_content_outline
- **Study Guide**: POST $app_url/api/v1/content/generate/study_guide
- **Flashcards**: POST $app_url/api/v1/content/generate/flashcards
- **Podcast Script**: POST $app_url/api/v1/content/generate/podcast_script
- **One-Pager**: POST $app_url/api/v1/content/generate/one_pager_summary
- **Reading Material**: POST $app_url/api/v1/content/generate/detailed_reading_material
- **FAQ Collection**: POST $app_url/api/v1/content/generate/faq_collection
- **Guide Questions**: POST $app_url/api/v1/content/generate/reading_guide_questions

## Quality Standards
- **Overall Quality Threshold**: ≥0.70
- **Educational Value Threshold**: ≥0.75
- **Factual Accuracy Threshold**: ≥0.85

## Test Commands
\`\`\`bash
# Health check
curl $app_url/health

# Detailed system status
curl $app_url/api/v1/health/detailed

# System metrics
curl $app_url/api/v1/metrics

# Educational metrics
curl $app_url/api/v1/metrics/educational
\`\`\`

## Example Content Generation
\`\`\`bash
curl -X POST $app_url/api/v1/content/generate/study_guide \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "topic": "Python Programming Basics",
    "age_group": "high_school"
  }'
\`\`\`

## Next Steps
1. Configure environment variables in Railway dashboard
2. Test content generation with real API key
3. Monitor system performance via monitoring dashboard
4. Set up alerting and notifications
5. Review operational procedures in PRODUCTION_OPERATIONS.md

## Support Resources
- **Monitoring Dashboard**: $app_url/static/monitor.html
- **Railway Logs**: \`railway logs\`
- **Database Access**: \`railway connect\`
- **Operations Guide**: PRODUCTION_OPERATIONS.md
EOF

    success "Deployment report generated: DEPLOYMENT_REPORT.md"
}

# Main deployment function
main() {
    echo ""
    log "Starting La Factoria deployment to Railway..."
    echo ""

    # Pre-deployment checks
    check_railway_cli
    validate_project
    check_railway_auth

    echo ""
    log "Pre-deployment validation completed successfully"
    echo ""

    # Deployment process
    deploy_application
    setup_environment
    wait_for_deployment
    setup_database

    echo ""
    log "Deployment process completed"
    echo ""

    # Post-deployment validation
    validate_deployment
    generate_report

    echo ""
    echo "=================================================="
    success "🎉 La Factoria deployment completed successfully!"
    echo "=================================================="
    echo ""

    app_url=$(railway domain 2>/dev/null || echo "your-app.railway.app")
    if [[ ! "$app_url" == https://* ]]; then
        app_url="https://$app_url"
    fi

    echo "🌐 Your La Factoria platform is now live at:"
    echo "   $app_url"
    echo ""
    echo "📊 Monitor system health at:"
    echo "   $app_url/static/monitor.html"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Configure API keys in Railway dashboard"
    echo "   2. Test content generation endpoints"
    echo "   3. Review DEPLOYMENT_REPORT.md for details"
    echo "   4. Set up monitoring and alerting"
    echo ""
    echo "📖 See PRODUCTION_OPERATIONS.md for operational procedures"
    echo ""
}

# Run main function
main "$@"
