QUERY_REWRITER_PROMPT = """Given the following conversation history between a user and the AI assistant, rephrase the follow-up user question into a standalone, dense search query suitable for vector similarity retrieval. Do NOT answer the question, only output the rewritten search query.

Conversation History:
{chat_history}

Follow-up User Question: {raw_query}

Standalone Vector Search Query:"""
