from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

#Caminhos base
BASE_DIR = Path(__file__)
DATA_DIR = BASE_DIR / "data"
MEM_DIR = DATA_DIR / "memory"
HIST_DIR = DATA_DIR / "history"
TOPIC_DIR = MEM_DIR / "topic"

#Cria diretórios se não existirem
for d in [MEM_DIR, HIST_DIR, TOPIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

#Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") #Docker
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

LLM_NUM_PREDICT = int(os.getenv("LLM_NUM_PREDICT", 256))
LLM_NUM_CTX = int(os.getenv("LLM_NUM_CTX", 2048))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
LLM_NUM_THREAD = int(os.getenv("LLM_NUM_THREAD", 4))

MEMORY_MAX_NOTES = int(os.getenv("MEMORY_MAX_NOTES", 20))
MEMORY_MAX_TOPICS = int(os.getenv("MEMORY_MAX_TOPICS", 5))
HISTORY_MAX_SEARCH = int(os.getenv("HISTORY_MAX_SEARCH", 10))

AGENT_MAX_HISTORY_TURNS = int(os.getenv("AGENT_MAX_HISTORY_TURNS", 3))
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", 10))