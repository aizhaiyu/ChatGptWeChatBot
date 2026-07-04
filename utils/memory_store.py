import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


@dataclass
class ChatMemory:
    session_id: str
    display_name: str
    facts: list
    summary: str
    recent_messages: list
    updated_at: str


class MemoryStore:
    def __init__(self, memory_dir, recent_limit=12, compress_threshold=16, enabled=True):
        base_dir = Path(memory_dir)
        if not base_dir.is_absolute():
            base_dir = PROJECT_ROOT / base_dir

        self.base_dir = base_dir
        self.recent_limit = max(2, int(recent_limit))
        self.compress_threshold = max(self.recent_limit + 2, int(compress_threshold))
        self.enabled = enabled
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load(self, session_id, display_name=''):
        if not self.enabled:
            return self._empty_memory(session_id, display_name)

        path = self._path_for(session_id)
        if not path.exists():
            return self._empty_memory(session_id, display_name)

        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load memory %s: %s", path, exc)
            return self._empty_memory(session_id, display_name)

        return ChatMemory(
            session_id=session_id,
            display_name=data.get('display_name') or display_name,
            facts=self._normalize_facts(data.get('facts')),
            summary=data.get('summary') or '',
            recent_messages=data.get('recent_messages') or [],
            updated_at=data.get('updated_at') or '',
        )

    def save(self, memory):
        if not self.enabled:
            return

        path = self._path_for(memory.session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'session_id': memory.session_id,
            'display_name': memory.display_name,
            'facts': memory.facts,
            'summary': memory.summary,
            'recent_messages': memory.recent_messages[-self.compress_threshold:],
            'updated_at': datetime.now().isoformat(timespec='seconds'),
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def append_turn(self, memory, user_text, assistant_text):
        if not self.enabled:
            return memory

        memory.recent_messages.extend([
            {'role': 'user', 'content': user_text},
            {'role': 'assistant', 'content': assistant_text},
        ])
        memory.updated_at = datetime.now().isoformat(timespec='seconds')
        return memory

    def should_compress(self, memory):
        return self.enabled and len(memory.recent_messages) >= self.compress_threshold

    def compress_if_needed(self, memory, compressor):
        if not self.should_compress(memory):
            return memory

        old_messages = memory.recent_messages[:-self.recent_limit]
        keep_messages = memory.recent_messages[-self.recent_limit:]
        if not old_messages:
            return memory

        try:
            update = compressor(memory.summary, memory.facts, old_messages)
            memory.summary = update.get('summary') or memory.summary
            memory.facts = self._normalize_facts(update.get('facts', memory.facts))
            memory.recent_messages = keep_messages
        except Exception as exc:
            logger.exception("Failed to compress memory for %s: %s", memory.session_id, exc)
            memory.recent_messages = memory.recent_messages[-self.compress_threshold:]
        return memory

    def _empty_memory(self, session_id, display_name):
        return ChatMemory(
            session_id=session_id,
            display_name=display_name,
            facts=[],
            summary='',
            recent_messages=[],
            updated_at='',
        )

    def _path_for(self, session_id):
        digest = hashlib.sha256(session_id.encode('utf-8')).hexdigest()
        return self.base_dir / f'{digest}.json'

    def _normalize_facts(self, facts):
        if not facts:
            return []
        if isinstance(facts, str):
            return [line.strip('- ').strip() for line in facts.splitlines() if line.strip()]
        if not isinstance(facts, list):
            return []

        normalized = []
        seen = set()
        for item in facts:
            if not isinstance(item, str):
                continue
            fact = item.strip()
            if not fact or fact in seen:
                continue
            normalized.append(fact)
            seen.add(fact)
        return normalized[:50]
