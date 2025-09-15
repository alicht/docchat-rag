from openai import OpenAI
import os

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
    async def generate_response(self, query: str, context: str) -> str:
        try:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
            If the context doesn't contain relevant information, say so."""
            
            user_prompt = f"""Context:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")