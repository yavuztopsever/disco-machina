#!/bin/bash
# Run all tests for the calculator project

# Set up colors for better visualization
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}Running all tests for Calculator Application${NC}"
echo -e "${BLUE}===============================================${NC}"

# Run unit tests
echo -e "\n${GREEN}Running Unit Tests...${NC}"
python -m pytest tests/unit -v

# Run integration tests
echo -e "\n${GREEN}Running Integration Tests...${NC}"
python -m pytest tests/integration -v

# Run end-to-end tests
echo -e "\n${GREEN}Running End-to-End Tests...${NC}"
python -m pytest tests/e2e -v

# Run User Acceptance Tests with Behave
echo -e "\n${YELLOW}Running User Acceptance Tests...${NC}"
if command -v behave &> /dev/null; then
    behave tests/uat/features
else
    echo "Behave not installed. Install with: pip install behave"
    echo "Then run: behave tests/uat/features"
fi

# Generate coverage report
echo -e "\n${GREEN}Generating Coverage Report...${NC}"
python -m pytest --cov=calculator --cov-report=term-missing

echo -e "\n${BLUE}===============================================${NC}"
echo -e "${BLUE}All tests completed${NC}"
echo -e "${BLUE}===============================================${NC}"