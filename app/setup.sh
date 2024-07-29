#!/bin/bash

# Modify with your preferred models
CHAT_MODEL=phi3
EMBED_MODEL=locusai/multi-qa-minilm-l6-cos-v1

# Function to echo a new line before and after a message
echoo() {
  echo ""
  echo "$1"
  echo ""
}

# cd to file directory
cd "$(dirname "$0")"


# # Instead of scripting docker-compose up (as you may need to download the images)
# # docker-compose up on a terminal and wait till the services are up and running
# # you can use `docker ps` to verify. Afterwards ./setup.sh
# # Bring up Docker Compose
# docker-compose up -d
# # Wait for the containers to be fully up and running
# # Adjust the sleep duration if necessary
# sleep 30


# Execute commands inside the ollama container
echoo "pulling olama models..."
docker-compose exec -e CHAT_MODEL="$CHAT_MODEL" -e EMBED_MODEL="$EMBED_MODEL" ollama bash -c "
  echoo() {
    echo ''
    echo \"\$1\"
    echo ''
  }

  echoo 'Pulling ${CHAT_MODEL}...'
  ollama pull ${CHAT_MODEL}

  echoo 'Pulling ${EMBED_MODEL}...'
  ollama pull ${EMBED_MODEL}
"


# Activate the conda environment and run setup.py
source activate dtc-llm-env
echoo "Setting up postgres & es..."
python setup.py install




