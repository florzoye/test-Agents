from langchain_core.prompts import PromptTemplate

class DialogPromptTemplates:
    @classmethod
    async def get_dialog_prompt(self) -> PromptTemplate:
        template = """
        Client Information:
        info: {client_info}

        new message: {message}
        """
        return PromptTemplate.from_template(template)

class SystemPromptTemplate:
    @classmethod
    async def get_system_prompt(self) -> PromptTemplate:
        template = """
        """
        return PromptTemplate.from_template(template)
