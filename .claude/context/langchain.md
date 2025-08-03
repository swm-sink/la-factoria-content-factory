# LangChain Integration Context

## Core Architecture

### Framework Purpose
- Develop applications powered by large language models (LLMs)
- Simplifies the entire LLM application lifecycle
- Provides standard interfaces and hundreds of provider integrations

### Key Components
- `langchain-core`: Base abstractions for chat models and prompts
- `langchain`: Chains, agents, retrieval strategies, and tools
- `langgraph`: Orchestration framework for building stateful applications
- `langsmith`: Monitoring, evaluation, and debugging tools

### Development Lifecycle
1. **Development**: Use open-source components and integrations
2. **Productionization**: Use LangSmith for monitoring and evaluation  
3. **Deployment**: Convert applications into production APIs

## Core Concepts

### LangChain Expression Language (LCEL)
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Basic chain composition
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = ChatOpenAI(model="gpt-3.5-turbo")
output_parser = StrOutputParser()

chain = prompt | model | output_parser

# Invoke the chain
result = chain.invoke({"topic": "programming"})
```

### Prompt Templates
```python
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# System + Human message template
system_template = "You are a helpful assistant that {task}."
human_template = "{user_input}"

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])

# Format the prompt
messages = chat_prompt.format_messages(
    task="generates educational content",
    user_input="Create a study guide about Python"
)
```

### Memory Systems
```python
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.messages import HumanMessage, AIMessage

# Buffer Memory - stores exact conversation
buffer_memory = ConversationBufferMemory(return_messages=True)
buffer_memory.chat_memory.add_user_message("Hello!")
buffer_memory.chat_memory.add_ai_message("Hi there!")

# Summary Memory - summarizes old conversations
summary_memory = ConversationSummaryMemory(
    llm=ChatOpenAI(temperature=0),
    return_messages=True
)

# Memory with message trimming for large conversations
from langchain_core.messages import trim_messages

def manage_memory(messages, max_tokens=1000):
    return trim_messages(
        messages,
        max_tokens=max_tokens,
        strategy="last",
        token_counter=len  # or use tiktoken for accurate counting
    )
```

## Retrieval Augmented Generation (RAG)

### Document Loading and Processing
```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load documents
loader = PyPDFLoader("document.pdf")
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
splits = text_splitter.split_documents(documents)

# Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)

# Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)
```

### RAG Chain Implementation
```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG Chain
rag_chain = (
    RunnableParallel({"context": retriever | format_docs, "question": RunnablePassthrough()})
    | ChatPromptTemplate.from_template("""
        Answer the question based only on the following context:
        
        {context}
        
        Question: {question}
        
        Answer:
    """)
    | model
    | StrOutputParser()
)

# Use the chain
answer = rag_chain.invoke("What is the main topic of the document?")
```

## Agents and Tools

### Tool Definition
```python
from langchain_core.tools import Tool
from langchain.agents import initialize_agent, AgentType
import requests

def get_weather(location: str) -> str:
    """Get current weather for a location."""
    # Mock weather API call
    return f"The weather in {location} is sunny and 75°F"

def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock web search
    return f"Search results for: {query}"

# Define tools
tools = [
    Tool(
        name="Weather",
        func=get_weather,
        description="Get current weather for a location"
    ),
    Tool(
        name="WebSearch", 
        func=search_web,
        description="Search the web for information"
    )
]
```

### Agent Implementation
```python
from langchain.agents import create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Agent prompt
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to tools."),
    MessagesPlaceholder("chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

# Create agent
agent = create_openai_functions_agent(
    llm=model,
    tools=tools,
    prompt=agent_prompt
)

# Agent executor
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Use the agent
result = agent_executor.invoke({
    "input": "What's the weather like in San Francisco and search for Python tutorials"
})
```

## Advanced Patterns

### Parallel Chain Execution
```python
from langchain_core.runnables import RunnableParallel

# Parallel processing
parallel_chain = RunnableParallel(
    joke=ChatPromptTemplate.from_template("Tell a joke about {topic}") | model | StrOutputParser(),
    poem=ChatPromptTemplate.from_template("Write a poem about {topic}") | model | StrOutputParser(),
    facts=ChatPromptTemplate.from_template("List 3 facts about {topic}") | model | StrOutputParser()
)

results = parallel_chain.invoke({"topic": "artificial intelligence"})
```

### Conditional Logic
```python
from langchain_core.runnables import RunnableBranch

def route_question(info):
    if "weather" in info["question"].lower():
        return "weather_chain"
    elif "math" in info["question"].lower():
        return "math_chain"
    else:
        return "general_chain"

# Conditional routing
branch = RunnableBranch(
    (lambda x: "weather" in x["question"].lower(), weather_chain),
    (lambda x: "math" in x["question"].lower(), math_chain),
    general_chain  # default
)
```

### Streaming Support
```python
# Streaming responses
async def stream_response(chain, input_data):
    async for chunk in chain.astream(input_data):
        print(chunk, end="", flush=True)

# Use with async
import asyncio
asyncio.run(stream_response(chain, {"topic": "Python"}))
```

## Production Patterns

### Error Handling
```python
from langchain_core.runnables import RunnableWithFallbacks

# Fallback chain
primary_chain = prompt | ChatOpenAI(model="gpt-4") | output_parser
fallback_chain = prompt | ChatOpenAI(model="gpt-3.5-turbo") | output_parser

chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])

# Retry logic
from langchain_core.runnables import RunnableRetry

retry_chain = RunnableRetry(
    bound=chain,
    max_attempt_number=3,
    wait_exponential_jitter=True
)
```

### Configuration Management
```python
from langchain_core.runnables import ConfigurableField

# Configurable model
configurable_model = ChatOpenAI(temperature=0).configurable_fields(
    temperature=ConfigurableField(
        id="temperature",
        name="LLM Temperature",
        description="Temperature for the LLM"
    ),
    model=ConfigurableField(
        id="model",
        name="LLM Model",
        description="The model to use"
    )
)

chain = prompt | configurable_model | output_parser

# Configure at runtime
result = chain.invoke(
    {"topic": "AI"},
    config={"configurable": {"temperature": 0.9, "model": "gpt-4"}}
)
```

### Batch Processing
```python
# Batch processing
batch_results = chain.batch([
    {"topic": "Python"},
    {"topic": "JavaScript"},
    {"topic": "Machine Learning"}
])

# Async batch processing
async def process_batch():
    results = await chain.abatch([
        {"topic": "Python"},
        {"topic": "JavaScript"}
    ])
    return results
```

## LangSmith Integration

### Tracing and Monitoring
```python
import os
from langsmith import traceable

# Set up LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "your-project-name"

@traceable
def custom_function(input_text):
    return chain.invoke({"topic": input_text})

# Add metadata to traces
result = chain.invoke(
    {"topic": "AI"},
    config={
        "metadata": {"user_id": "123", "session_id": "abc"},
        "tags": ["production", "content-generation"]
    }
)
```

### Evaluation
```python
from langsmith.evaluation import evaluate

def correctness_evaluator(run, example):
    # Custom evaluation logic
    prediction = run.outputs["output"]
    reference = example.outputs["expected"]
    return {"score": 1 if prediction == reference else 0}

# Run evaluation
results = evaluate(
    lambda inputs: chain.invoke(inputs),
    data="your-dataset-name",
    evaluators=[correctness_evaluator]
)
```

## Best Practices

### Performance Optimization
1. **Use LCEL for chain composition** - more efficient than legacy chains
2. **Implement streaming** for better user experience  
3. **Batch operations** when processing multiple inputs
4. **Use async/await** for I/O bound operations
5. **Cache embeddings** and expensive computations

### Memory Management
1. **Trim conversation history** for long conversations
2. **Use summary memory** for better context management
3. **Implement token counting** to stay within limits
4. **Clear memory** when appropriate

### Error Handling
1. **Implement fallback models** for reliability
2. **Add retry logic** with exponential backoff
3. **Handle parsing errors** gracefully
4. **Log errors** for debugging

### Security
1. **Validate inputs** before processing
2. **Sanitize outputs** to prevent injection
3. **Use environment variables** for API keys
4. **Implement rate limiting** for production

## Sources
6. LangChain Python Documentation - Introduction
7. LangChain Tutorials and How-to Guides
8. LangChain Expression Language (LCEL) Documentation
9. LangSmith Tracing and Evaluation Documentation
10. LangGraph Stateful Applications Documentation