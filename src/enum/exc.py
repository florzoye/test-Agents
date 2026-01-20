from enum import StrEnum, Enum

class AgentEnum(StrEnum):
    DIALOG = "DIALOG AGENT"
    SUMMARY = "SUMMARY AGENT"
    RESEARCH = "RESEARCH AGENT"

class ExceptionHandler(StrEnum):
    EXECUTE_ERROR = '[EXECUTE ERROR]'
    INIT_ERROR = '[INITIALIZATION ERROR]'

