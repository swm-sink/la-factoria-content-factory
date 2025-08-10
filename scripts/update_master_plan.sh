#!/bin/bash

# Master Plan Update Script
# =========================
# Regenerates the markdown report from master_plan.yaml

echo "🔄 Updating Master Plan Report..."
echo ""

# Check if master_plan.yaml exists
if [ ! -f "master_plan.yaml" ]; then
    echo "❌ Error: master_plan.yaml not found"
    echo "Please ensure the master plan YAML file exists in the current directory."
    exit 1
fi

# Check if the generator script exists
if [ ! -f "generate_master_plan_report.py" ]; then
    echo "❌ Error: generate_master_plan_report.py not found"
    echo "Please ensure the generator script exists in the current directory."
    exit 1
fi

# Run the generator
python3 generate_master_plan_report.py

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Master plan report updated successfully!"
    echo "📁 View the report: MASTER_PLAN_REPORT.md"
    
    # Show basic stats
    if [ -f "MASTER_PLAN_REPORT.md" ]; then
        word_count=$(wc -w < MASTER_PLAN_REPORT.md)
        line_count=$(wc -l < MASTER_PLAN_REPORT.md)
        echo "📊 Report stats: $word_count words, $line_count lines"
    fi
    
    echo ""
    echo "💡 Tip: Add to git and commit your changes:"
    echo "   git add master_plan.yaml MASTER_PLAN_REPORT.md"
    echo "   git commit -m 'docs: update master plan and progress report'"
    
else
    echo ""
    echo "❌ Error: Failed to generate master plan report"
    exit 1
fi