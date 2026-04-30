"""
Chat Service - AI conversation and answer generation
Provides competition-optimized answer generation using OpenAI models
Features: Rate limiting, retry logic, multilingual support
"""

import os
import asyncio
import random
from asyncio import Semaphore
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.logger import get_logger

load_dotenv()

log = get_logger("chat")

# AI model configuration
GENERATION_OPENAI_API_KEY = os.getenv("GENERATION_OPENAI_API_KEY")
OPENAI_LLM_MODEL = "o4-mini"
MAX_CONCURRENT_LLM = 3
LLM_RETRY_DELAY = 2.0
MAX_RETRIES = 3

# Initialize clients and rate limiting
openai_client = AsyncOpenAI(api_key=GENERATION_OPENAI_API_KEY)
llm_semaphore = Semaphore(MAX_CONCURRENT_LLM)


async def gemini_chat(question: str, context_snippets: List[str]) -> str:
    """
    Generate answers using Gemini 2.5 Pro with rate limiting
    
    Args:
        question: User question to answer
        context_snippets: Relevant document excerpts for context
        
    Returns:
        Generated answer with inline citations
    """
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build context from retrieved document snippets
        context = "\n---\n".join(context_snippets)
        
        # Create prompt for Track B compliance
        prompt = f"""Based on the following document excerpts, please answer the question. Use inline citations [1], [2], etc. to reference the relevant excerpts.

Question: {question}

Document excerpts:
{context}

Please provide a comprehensive answer with inline citations where appropriate. Be precise and only use information from the provided excerpts."""

        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Could not generate an answer from the model."
            
    except Exception as e:
        log.error("gemini_chat failed: %s", e)
        # Fallback to OpenAI if Gemini fails
        return await openai_chat(question, context_snippets)

async def openai_chat(question: str, context_snippets: List[str]) -> str:
    """
    Generate answers using OpenAI with rate limiting (fallback)
    
    Args:
        question: User question to answer
        context_snippets: Relevant document excerpts for context
        
    Returns:
        Generated answer
    """
    async with llm_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                # Build context from retrieved document snippets
                context = "\n---\n".join(context_snippets)

                # Create Track B compliant prompt
                prompt = f"""Based on the following document excerpts, please answer the question. Use inline citations [1], [2], etc. to reference the relevant excerpts.

Question: {question}

Document excerpts:
{context}

Please provide a comprehensive answer with inline citations where appropriate."""

                # Generate response using OpenAI
                response = await openai_client.chat.completions.create(
                    model=OPENAI_LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document excerpts. Always use inline citations [1], [2], etc. to reference the source material."},
                        {"role": "user", "content": prompt},
                    ],
                )

                # Extract and clean the response
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    answer = choice.message.content.strip()
                    return answer

                # Fallback if no answer found
                return "Could not generate an answer from the model."

            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = LLM_RETRY_DELAY * (2**attempt) + random.uniform(0, 1)
                        log.warning("LLM rate limit hit, retrying in %.2fs (attempt %d)", delay, attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                log.error("openai_chat failed: %s", e)
                return f"Error generating response: {str(e)}"


async def intelligent_agent_chat(
    question: str,
    document_content: str,
    url_data: Dict[str, Dict[str, Any]],
    context_snippets: List[str],
) -> str:
    """
    Enhanced agent for complex multi-step document processing
    
    Args:
        question: User question to answer
        document_content: Full document text for context
        url_data: Fetched URL content and metadata
        context_snippets: Retrieved relevant document excerpts
        
    Returns:
        Comprehensive answer with multi-step reasoning
    """
    async with llm_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                # Build comprehensive context
                context = "\n---\n".join(context_snippets)

                # Prepare URL information for multi-step processing
                url_info = ""
                if url_data:
                    url_info = "\n\nURL RESPONSES FETCHED FROM DOCUMENT:\n"
                    for url, data in url_data.items():
                        if data["success"]:
                            url_info += f"\nURL: {url}\n"
                            url_info += f"Status: {data['status_code']}\n"
                            url_info += f"Content Type: {data['content_type']}\n"
                            url_info += f"Response Content: {data['content'][:2000]}...\n"
                            url_info += "---\n"
                        else:
                            url_info += f"\nURL: {url}\nError: {data['error']}\n---\n"

                # Create enhanced agent prompt
                prompt = f"""
<system>
You are an intelligent document analysis agent with the following capabilities:

CORE ABILITIES:
1. **Multi-step Task Execution**: Follow complex instructions that involve multiple steps
2. **URL Integration**: Use data fetched from URLs mentioned in documents to make informed decisions
3. **Information Retention**: Remember and use information gathered from previous steps
4. **Decision Making**: Make logical decisions based on combined document and web data
5. **Instruction Following**: Carefully follow specific instructions mentioned in documents

RESPONSE GUIDELINES:
1. **Analyze the document content** to understand any step-by-step instructions
2. **Use URL response data** when making decisions or following instructions
3. **Follow the logical flow** mentioned in the document (e.g., if document says "first do X, then do Y based on result of X")
4. **Combine information** from both document content and URL responses
5. **Provide complete answers** that address the question while following document instructions
6. **Be precise and accurate** - competition answers need to be exact
7. **MULTILINGUAL SUPPORT**: Detect and respond in the EXACT same language as the question asked (Hindi, Malayalam, English, etc.)
8. **STRICT DOCUMENT ADHERENCE**: Base answers ONLY on document content and URL data - make NO assumptions or interpretations beyond what is explicitly stated

- Give direct, natural answers (1-3 sentences for simple questions)
- For complex multi-step processes, provide the final answer while showing key reasoning
- Use information from URL responses when relevant to the question
- Follow any specific answer format mentioned in the document
- NEVER include newline characters (\n) or line breaks in your response
- Provide answers as single continuous text without formatting
- **LANGUAGE MATCHING**: Respond in the EXACT same language as the question asked (English/Hindi/Malayalam/etc.)
- **NO ASSUMPTIONS**: Only use information explicitly stated in documents or URL responses
CRITICAL: If the document contains step-by-step instructions that involve URLs, follow those instructions precisely using the URL response data provided.
</system>

<document_content>
{document_content[:5000]}  <!-- Truncate very long documents -->
</document_content>

<retrieved_relevant_snippets>
{context}
</retrieved_relevant_snippets>

{url_info}

<user_question>
{question}
</user_question>

<instruction>
Analyze the document and URL data, follow any multi-step instructions mentioned in the document, and provide a comprehensive answer to the user's question. CRITICAL: Respond in the EXACT same language as the source document and base your answer ONLY on explicit document content and URL data without any assumptions or interpretations. If the document contains specific instructions involving URLs, execute those instructions using the URL response data and provide the final result.
</instruction>
"""

                response = await openai_client.chat.completions.create(
                    model=OPENAI_LLM_MODEL,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": question},
                    ],
                )

                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    answer = choice.message.content.strip()
                    # Remove any newlines or extra whitespace for clean output
                    answer = " ".join(answer.split())
                    return answer

                return "Could not generate an answer from the intelligent agent."

            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = LLM_RETRY_DELAY * (2**attempt) + random.uniform(0, 1)
                        log.warning("intelligent agent rate limit hit, retrying in %.2fs (attempt %d)", delay, attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                log.error("intelligent_agent_chat failed: %s", e)
                return f"Error generating intelligent response: {str(e)}"


async def direct_context_answer(
    question: str, 
    content: str, 
    url_text: str = "", 
    model_preference: str = "gemini"
) -> str:
    """
    Generate answer using direct context for small documents (optimization)
    Bypasses chunking and vector search when content fits in model context
    
    Args:
        question: User question to answer
        content: Main document content
        url_text: Additional URL content if available
        model_preference: Model choice ("gemini" or "openai")
        
    Returns:
        Generated answer string
    """
    try:
        # Combine all available content
        full_context = content
        if url_text:
            full_context += f"\n\n--- Additional Web Content ---\n{url_text}"

        # Use direct context as single snippet
        context_snippets = [full_context]

        # Route to appropriate model
        if model_preference == "gemini":
            answer = await gemini_chat(question, context_snippets)
        else:
            answer = await intelligent_agent_chat(
                question, full_context, {}, context_snippets
            )

        return answer.strip() if answer else "No response generated"

    except Exception as e:
        log.error("direct_context_answer failed: %s", e)
        return f"Error generating direct answer: {str(e)}"
