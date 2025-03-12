#!/bin/bash
#
# Disco-Machina Installation Script
# Installs and configures the Disco-Machina terminal client for the Dev Team API
#
# Created by Yavuz Topsever (https://github.com/yavuztopsever)
#

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║   ____  _                 __  __            _     _                      ║"
echo "║  |  _ \(_)___  ___ ___   |  \/  | __ _  ___| |__ (_)_ __   __ _         ║"
echo "║  | | | | / __|/ __/ _ \  | |\/| |/ _` |/ __| '_ \| | '_ \ / _` |        ║"
echo "║  | |_| | \__ \ (_| (_) | | |  | | (_| | (__| | | | | | | | (_| |        ║"
echo "║  |____/|_|___/\___\___/  |_|  |_|\__,_|\___|_| |_|_|_| |_|\__,_|        ║"
echo "║                                                                          ║"
echo "║                                                                          ║"
echo "║                  AI-Powered Dev Team Agents                              ║"
echo "║           Building the Future, One Line at a Time                        ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}Disco-Machina Installation${NC}\n"
echo -e "This script will install Disco-Machina and configure it for your system.\n"

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Python 3 found!${NC}"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Python found!${NC}"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "Python version: ${GREEN}$PYTHON_VERSION${NC}"

if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or higher is required.${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Installing required packages...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt

# Create executable script
echo -e "\n${YELLOW}Creating discomachina executable...${NC}"
EXEC_PATH="$HOME/.local/bin/discomachina"
mkdir -p "$(dirname "$EXEC_PATH")"

cat > "$EXEC_PATH" << EOF
#!/bin/bash
$PYTHON_CMD "$(pwd)/terminal_client.py" "\$@"
EOF

chmod +x "$EXEC_PATH"

# Check if PATH contains ~/.local/bin
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "\n${YELLOW}Adding ~/.local/bin to your PATH...${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
    echo -e "${GREEN}Added to PATH in .bashrc and .zshrc (if it exists)${NC}"
    echo -e "${YELLOW}Please restart your terminal or run 'source ~/.bashrc' to apply changes.${NC}"
fi

# Create alternative scripts
echo -e "\n${YELLOW}Creating alternative chat clients...${NC}"

chmod +x simple_chat.py
chmod +x robust_chat.py
chmod +x test_chat.py

# Check if the server is running
echo -e "\n${YELLOW}Checking if server is running...${NC}"
if $PYTHON_CMD -c "import requests; exit(0) if requests.get('http://localhost:8000/health', timeout=2).status_code == 200 else exit(1)" 2>/dev/null; then
    echo -e "${GREEN}Server is running!${NC}"
else
    echo -e "${YELLOW}Server is not running. Starting server...${NC}"
    echo -e "You can start the server with: ${CYAN}python -m src.dev_team.server${NC}"
    
    # Ask if they want to use Docker
    read -p "Would you like to start the server with Docker? (y/n): " use_docker
    if [[ "$use_docker" == "y" ]]; then
        echo -e "\n${YELLOW}Starting server with Docker...${NC}"
        if command -v docker-compose &>/dev/null; then
            docker-compose up -d
            echo -e "${GREEN}Server started with Docker!${NC}"
        elif command -v docker &>/dev/null && command -v compose &>/dev/null; then
            docker compose up -d
            echo -e "${GREEN}Server started with Docker!${NC}"
        else
            echo -e "${RED}Docker or docker-compose not found. Please install Docker and try again.${NC}"
            echo -e "Server not started."
        fi
    fi
fi

# Installation complete
echo -e "\n${GREEN}Disco-Machina installation complete!${NC}"
echo -e "You can run Disco-Machina with: ${CYAN}discomachina${NC}"
echo -e "Or directly with: ${CYAN}python terminal_client.py${NC}"
echo -e "\nAlternative chat clients:"
echo -e "Simple chat: ${CYAN}./simple_chat.py${NC}"
echo -e "Robust chat: ${CYAN}./robust_chat.py${NC}"
echo -e "Test chat:   ${CYAN}./test_chat.py${NC}"

echo -e "\n${YELLOW}For documentation, see:${NC}"
echo -e "- ${CYAN}docs/client_usage.md${NC} - Terminal client usage guide"
echo -e "- ${CYAN}docs/terminal_interaction_guide.md${NC} - Detailed interaction guide"

echo -e "\n${GREEN}Enjoy using Disco-Machina!${NC}"