from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

    def generate_with_context(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[str],
    ) -> str:
        """
        Default behavior: join context into the prompt.
        Providers can override if needed.
        """
        context_text = "\n\n".join([f"- {c}" for c in context_chunks])
        final_prompt = f"""Use the context below to answer the user.

CONTEXT:
{context_text}

USER QUESTION:
{user_prompt}

Answer clearly and concisely. If you don't know from context, say you don't know."""
        return self.generate(system_prompt, final_prompt)
