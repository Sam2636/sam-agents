Compress-Archive -Path .  -DestinationPath "SampleRepo.zip"


--create the folder structure

# Create folders
New-Item -ItemType Directory -Path legacy_doc_agent
New-Item -ItemType Directory -Path legacy_doc_agent\core
New-Item -ItemType Directory -Path legacy_doc_agent\workers
New-Item -ItemType Directory -Path legacy_doc_agent\utils

# Create files
New-Item -ItemType File -Path legacy_doc_agent\config.py
New-Item -ItemType File -Path legacy_doc_agent\main.py
New-Item -ItemType File -Path legacy_doc_agent\requirements.txt

New-Item -ItemType File -Path legacy_doc_agent\core\agent_manager.py
New-Item -ItemType File -Path legacy_doc_agent\core\metrics.py
New-Item -ItemType File -Path legacy_doc_agent\core\tokenizer.py

New-Item -ItemType File -Path legacy_doc_agent\workers\folder_agent.py
New-Item -ItemType File -Path legacy_doc_agent\workers\file_agent.py
New-Item -ItemType File -Path legacy_doc_agent\workers\doc_generator.py

New-Item -ItemType File -Path legacy_doc_agent\utils\fs_utils.py
New-Item -ItemType File -Path legacy_doc_agent\utils\logger.py


# front end setup

# Create project
npm create vite@latest legacy-doc-frontend -- --template react

cd legacy-doc-frontend

# Install dependencies
npm install axios react-router-dom @mui/material @mui/icons-material
