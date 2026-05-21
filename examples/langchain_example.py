"""LangChain example. Install langchain packages separately and run through HTTPS_PROXY."""

from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
print(model.invoke("Say hello from llm-spy.").content)
