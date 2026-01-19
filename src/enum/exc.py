from enum import StrEnum, Enum

class AgentEnum(StrEnum):
    DIALOG = "DIALOG AGENT"
    SUMMARY = "SUMMARY AGENT"
    RESEARCH = "RESEARCH AGENT"

class ExceptionHandler(StrEnum):
    EXECUTE_ERROR = '[EXECUTE ERROR]'
    INIT_ERROR = '[INITIALIZATION ERROR]'

from src.exceptions.agent_exp import LLMException, AgentExecutionException # circulate import
class RetryExceptionsEnum(Enum):
    AGENT_EXCEPTIONS =  (LLMException, AgentExecutionException, TimeoutError, ConnectionError)