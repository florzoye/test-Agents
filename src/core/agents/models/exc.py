from enum import StrEnum

class AgentEnum(StrEnum):
    DIALOG = "DIALOG AGENT"
    SUMMARY = "SUMMARY AGENT"

class ExceptionHandler(StrEnum):
    EXECUTE_ERROR = '[EXECUTE ERROR]'
    INIT_ERROR = '[INITIALIZATION ERROR]'

class AgentException(Exception):
    def __init__(self, message: str, agent: AgentEnum, exp: Exception):
        self.exc = exp
        self.agent = agent
        self.message = message
        super().__init__(f"[{agent}] {message} - {exp}")
    
    def __str__(self):
        return f"[{self.agent}] {self.message} - {self.exc}"

class AgentInitializationException(AgentException):
    def __init__(self, agent: AgentEnum, exp: Exception, message: str = "Ошибка при инициализации агента", ):
        super().__init__(message=message, agent=agent,exp=exp)

class AgentExecutionException(AgentException):
    def __init__(self, agent: AgentEnum, exp: Exception, message: str = "Ошибка при выполнении execute"):
        super().__init__(message=message, agent=agent,exp=exp)


class LLMException(AgentException):
    def __init__(self, agent: AgentEnum, exp: Exception, message: str):
        super().__init__(message=message, agent=agent,exp=exp)

