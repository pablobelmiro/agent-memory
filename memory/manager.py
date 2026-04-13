import re
from memory.layer1_core   import CoreMemory
from memory.layer2_topics import TopicMemory
from memory.layer3_history import HistoryMemory

SAVE_PATTERN = re.compile(r'\[SAVE:\s*(.+?)\]', re.IGNORECASE)

class MemoryManager:
    """Interface única para as 3 camadas de memória."""

    def __init__(self):
        self.core = CoreMemory()
        self.topics = TopicMemory()
        self.history = HistoryMemory()

    def load_core(self) -> dict:
        return self.core.load()

    def load_relevant_topics(self, user_input: str) -> list[str]:
        """Camada 2: carrega tópicos cujos nomes aparecem no input."""
        return self.topics.load_relevant(user_input)

    def extract_and_save(self, user_text, assistant_text):
        data = self.core.load()

        # extração rápida por regex (sem custo de LLM)
        patterns = {
            "name":     r"(?:me chamo|meu nome é|sou o|sou a)\s+(\w+)",
            "job":      r"(?:trabalho como|sou)\s+([a-zA-Záéíóúãõ\s]+?)(?:\.|,|$)",
            "likes":    r"(?:gosto de|adoro)\s+(.+?)(?:\.|,|$)",
        }

        for key, pat in patterns:
            m = re.search(pat, user_text.load())
            if m:
                data.setdefault("facts", {})[key] = m.group(1).strip()

        # fatos que o modelo marcou explicitamente com [SAVE: ...]
        for fact in SAVE_PATTERN.findall(assistant_text):
            data.setdefault("notes", [])
            if fact not in data["notes"]:
                data["notes"].append(fact)

        self.core.save(data)

    def append_history(self, role: str, content: str):
        self.history.append(role, content)

    def search_history(self, term: str) -> list[dict]:
        return self.history.search(term)