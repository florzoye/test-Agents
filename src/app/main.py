import asyncio
from fastapi import FastAPI
from chain import MultiAgentChain
from src.app.routers import telegram

async def lifespan(app: FastAPI):
    chain = MultiAgentChain()
    graph = await chain.build_workflow()

    app.state.agent_task = asyncio.create_task(
        graph.ainvoke({})
    )

    print("🚀 Агент запущен")

    yield  

    task = getattr(app.state, "agent_task", None)
    if task:
        task.cancel()
        print("🛑 Агент остановлен")

app = FastAPI(title="Telegram Webhook", lifespan=lifespan)
app.include_router(telegram.router)