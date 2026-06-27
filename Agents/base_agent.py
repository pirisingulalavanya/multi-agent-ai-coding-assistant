from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv
from loguru import logger
import os

load_dotenv()

try:
    _langfuse_client = get_client()
    if _langfuse_client.auth_check():
        logger.info("Langfuse: authenticated, tracing enabled")
        langfuse_handler = CallbackHandler()
    else:
        logger.warning("Langfuse: authentication failed, tracing disabled")
        langfuse_handler = None
except Exception as e:
    logger.warning(f"Langfuse init failed, tracing disabled: {e}")
    langfuse_handler = None


class BaseAgent:
    def __init__(self, system_prompt: str, agent_name: str):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.chat_history = []
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.1,
            max_tokens=600,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        self.chain = self.prompt | self.llm

    def run(self, input_text: str, context: dict = {}) -> str:
        try:
            enriched_input = self._enrich_input(input_text, context)
            logger.info(f"[{self.agent_name}] Processing...")

            invoke_config = {}
            if langfuse_handler is not None:
                invoke_config["callbacks"] = [langfuse_handler]
                invoke_config["metadata"] = {
                    "langfuse_tags": [self.agent_name],
                    "langfuse_session_id": context.get("session_id", "untagged"),
                }

            response = self.chain.invoke(
                {
                    "input": enriched_input,
                    "chat_history": self.chat_history[-6:],
                },
                config=invoke_config,
            )
            content = response.content
            self.chat_history.append(HumanMessage(content=enriched_input))
            self.chat_history.append(AIMessage(content=content))
            logger.info(f"[{self.agent_name}] Done")
            return content
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error: {e}")
            return f"Error in {self.agent_name}: {str(e)}"

    def _enrich_input(self, input_text: str, context: dict) -> str:
        if not context:
            return input_text
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items() if v])
        return f"Context:\n{context_str}\n\nTask:\n{input_text}"
