#!/bin/bash
# Complete automated test for Quiz Service

set -e

cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧪 Quiz Service Automated Test${NC}"
echo ""

# Set environment variables
export OPENAI_API_KEY="dummy-key-for-testing"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="quiz_service"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
export KAFKA_BOOTSTRAP_SERVERS="localhost:39092"

# Start service in background
echo -e "${YELLOW}Starting Quiz Service...${NC}"
venv/bin/uvicorn app:app --host 0.0.0.0 --port 8003 > /tmp/quiz-service.log 2>&1 &
SERVICE_PID=$!

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Function to cleanup
cleanup() {
    echo -e "\n${YELLOW}Stopping service...${NC}"
    kill $SERVICE_PID 2>/dev/null || true
    wait $SERVICE_PID 2>/dev/null || true
}

trap cleanup EXIT

# Test 1: Health check
echo -e "${YELLOW}1. Testing Health Endpoint...${NC}"
HEALTH=$(curl -s http://localhost:8003/health)
if echo $HEALTH | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Response: $HEALTH"
    exit 1
fi
echo ""

# Test 2: Generate quiz
echo -e "${YELLOW}2. Generating Quiz...${NC}"
QUIZ_RESPONSE=$(curl -s -X POST http://localhost:8003/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-doc-'$(date +%s)'",
    "notes": "Python is a high-level programming language known for simplicity. It supports object-oriented programming and has extensive libraries for data science, web development, and automation. Python uses indentation for code blocks.",
    "title": "Python Basics Test",
    "num_questions": 5,
    "difficulty": "medium",
    "question_types": ["multiple_choice", "true_false", "short_answer"]
  }')

if echo $QUIZ_RESPONSE | grep -q '"id"'; then
    QUIZ_ID=$(echo $QUIZ_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    echo -e "${GREEN}✅ Quiz generated successfully${NC}"
    echo "Quiz ID: $QUIZ_ID"
else
    echo -e "${RED}❌ Quiz generation failed${NC}"
    echo "Response: $QUIZ_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Get quiz
echo -e "${YELLOW}3. Retrieving Quiz...${NC}"
QUIZ_DATA=$(curl -s http://localhost:8003/api/quiz/$QUIZ_ID)
if echo $QUIZ_DATA | grep -q '"id"'; then
    echo -e "${GREEN}✅ Quiz retrieved successfully${NC}"
else
    echo -e "${RED}❌ Quiz retrieval failed${NC}"
    exit 1
fi
echo ""

# Test 4: Submit answers
echo -e "${YELLOW}4. Submitting Answers...${NC}"
SUBMIT_RESPONSE=$(curl -s -X POST http://localhost:8003/api/quiz/$QUIZ_ID/submit \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "0": "A",
      "1": "True",
      "2": "Python is a programming language",
      "3": "B",
      "4": "False"
    },
    "user_id": "test-user-'$(date +%s)'"
  }')

if echo $SUBMIT_RESPONSE | grep -q '"response_id"'; then
    RESPONSE_ID=$(echo $SUBMIT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['response_id'])")
    SCORE=$(echo $SUBMIT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['score_percentage'])")
    echo -e "${GREEN}✅ Answers submitted successfully${NC}"
    echo "Response ID: $RESPONSE_ID"
    echo "Score: $SCORE%"
else
    echo -e "${RED}❌ Answer submission failed${NC}"
    echo "Response: $SUBMIT_RESPONSE"
    exit 1
fi
echo ""

# Test 5: Get results
echo -e "${YELLOW}5. Getting Quiz Results...${NC}"
RESULTS=$(curl -s "http://localhost:8003/api/quiz/$QUIZ_ID/results")
if echo $RESULTS | grep -q '"response_id"'; then
    echo -e "${GREEN}✅ Results retrieved successfully${NC}"
else
    echo -e "${RED}❌ Results retrieval failed${NC}"
    exit 1
fi
echo ""

# Test 6: Get history
echo -e "${YELLOW}6. Getting Quiz History...${NC}"
HISTORY=$(curl -s "http://localhost:8003/api/quiz/history")
if echo $HISTORY | grep -q '\['; then
    echo -e "${GREEN}✅ History retrieved successfully${NC}"
else
    echo -e "${RED}❌ History retrieval failed${NC}"
    exit 1
fi
echo ""

# Test 7: List quizzes
echo -e "${YELLOW}7. Listing All Quizzes...${NC}"
ALL_QUIZZES=$(curl -s "http://localhost:8003/api/quiz")
if echo $ALL_QUIZZES | grep -q '\['; then
    echo -e "${GREEN}✅ Quizzes listed successfully${NC}"
else
    echo -e "${RED}❌ Listing quizzes failed${NC}"
    exit 1
fi
echo ""

# Test 8: Delete quiz
echo -e "${YELLOW}8. Deleting Quiz...${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE http://localhost:8003/api/quiz/$QUIZ_ID)
if echo $DELETE_RESPONSE | grep -q '"deleted"'; then
    echo -e "${GREEN}✅ Quiz deleted successfully${NC}"
else
    echo -e "${RED}❌ Quiz deletion failed${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "✅ Health check"
echo "✅ Quiz generation (multiple question types)"
echo "✅ Quiz retrieval"
echo "✅ Answer submission with scoring"
echo "✅ Results with feedback"
echo "✅ Quiz history"
echo "✅ List quizzes"
echo "✅ Delete quiz"
echo ""
echo -e "${GREEN}Quiz Service is working correctly! ✅${NC}"
