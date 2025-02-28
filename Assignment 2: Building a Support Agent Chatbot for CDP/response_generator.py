from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub

class ResponseGenerator:
    def __init__(self, api_token=None):
        # Initialize LLM - use Hugging Face for this example
        self.llm = HuggingFaceHub(
            repo_id="google/flan-t5-xl",  
            huggingfacehub_api_token=api_token
        )
        
        # Define prompt templates
        self.how_to_template = PromptTemplate(
            input_variables=["question", "cdp", "context"],
            template="""
            You are a helpful customer support assistant for Customer Data Platforms (CDPs).
            
            A user has asked the following question about {cdp}:
            {question}
            
            Based on the documentation, here is the relevant information:
            {context}
            
            Please provide a clear, step-by-step answer to the user's question.
            Format your response with appropriate headings, bullet points, and code examples if relevant.
            """
        )
        
        self.comparison_template = PromptTemplate(
            input_variables=["question", "cdps", "context"],
            template="""
            You are a helpful customer support assistant for Customer Data Platforms (CDPs).
            
            A user has asked a comparison question:
            {question}
            
            This question involves comparing these CDPs: {cdps}
            
            Based on the documentation, here is the relevant information:
            {context}
            
            Please provide a clear comparison that highlights the similarities and differences between the CDPs
            regarding the specific aspect the user is asking about.
            Format your response with appropriate headings and bullet points for each CDP.
            """
        )
        
        self.ambiguous_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            You are a helpful customer support assistant for Customer Data Platforms (CDPs).
            
            A user has asked the following question, but it's not clear which CDP they're referring to:
            {question}
            
            Based on the documentation, here is the relevant information from various CDPs:
            {context}
            
            Please provide the most helpful answer you can, clarifying which CDP each part of your response refers to.
            If appropriate, ask the user to specify which CDP they're interested in.
            """
        )
        
        self.fallback_template = PromptTemplate(
            input_variables=["question"],
            template="""
            You are a helpful customer support assistant for Customer Data Platforms (CDPs).
            
            A user has asked the following question:
            {question}
            
            This question doesn't appear to be related to CDP how-to instructions.
            
            Please provide a polite response explaining that you're specialized in answering questions about 
            how to use Segment, mParticle, Lytics, and Zeotap CDPs, and ask if they have any questions about those topics.
            """
        )
        
        # Create LLM chains
        self.how_to_chain = LLMChain(llm=self.llm, prompt=self.how_to_template)
        self.comparison_chain = LLMChain(llm=self.llm, prompt=self.comparison_template)
        self.ambiguous_chain = LLMChain(llm=self.llm, prompt=self.ambiguous_template)
        self.fallback_chain = LLMChain(llm=self.llm, prompt=self.fallback_template)
    
    def generate_response(self, question_info, retrieved_docs=None):
        """Generate a response based on question classification and retrieved documents."""
        
        if question_info["type"] == "how-to" and retrieved_docs:
            # Combine document content
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Generate response
            response = self.how_to_chain.run(
                question=question_info["question"],
                cdp=question_info["cdp"],
                context=context
            )
            return response
            
        elif question_info["type"] == "comparison" and retrieved_docs:
            # Combine document content
            context = "\n\n".join([f"CDP: {doc.metadata['cdp']}\n{doc.page_content}" for doc in retrieved_docs])
            
            # Generate response
            response = self.comparison_chain.run(
                question=question_info["question"],
                cdps=", ".join(question_info["cdps"]),
                context=context
            )
            return response
            
        elif question_info["type"] == "ambiguous" and retrieved_docs:
            # Combine document content
            context = "\n\n".join([f"CDP: {doc.metadata['cdp']}\n{doc.page_content}" for doc in retrieved_docs])
            
            # Generate response
            response = self.ambiguous_chain.run(
                question=question_info["question"],
                context=context
            )
            return response
            
        else:  # unrelated or no docs retrieved
            response = self.fallback_chain.run(
                question=question_info["question"]
            )
            return response
