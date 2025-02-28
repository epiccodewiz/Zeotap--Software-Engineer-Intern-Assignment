import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class AdvancedQuestionHandler:
    def __init__(self, llm, vector_db):
        self.llm = llm
        self.vector_db = vector_db
        
        # Define patterns for different types of advanced questions
        self.advanced_patterns = {
            "implementation": [
                r"(advanced|complex) (implementation|setup|configuration)",
                r"enterprise (setup|implementation)",
                r"(multi|multiple) (environment|tenant)",
                r"(custom|advanced) (tracking|integration)"
            ],
            "troubleshooting": [
                r"(troubleshoot|debug|fix|issue|problem|error)",
                r"not (working|functioning|sending data)",
                r"data (quality|validation|inconsistency)"
            ],
            "best_practices": [
                r"best (practice|approach|way)",
                r"(optimal|optimized|efficient) (setup|configuration)",
                r"(recommendation|guideline)",
                r"(secure|security)"
            ],
            "migration": [
                r"(migrate|migration|transfer|move) (from|to|between)",
                r"switch(ing)? (from|to|between)",
                r"transition(ing)? (from|to|between)"
            ]
        }
        
        # Prompts for different types of advanced questions
        self.advanced_prompts = {
            "implementation": PromptTemplate(
                input_variables=["question", "cdp", "context"],
                template="""
                You are an expert CDP implementation specialist for {cdp}.
                
                A user has asked an advanced implementation question:
                {question}
                
                Based on the documentation, here is the relevant information:
                {context}
                
                Please provide a detailed, step-by-step answer that addresses the advanced implementation scenario.
                Include code snippets or configuration examples where appropriate.
                Highlight any prerequisites, dependencies, or potential challenges.
                """
            ),
            "troubleshooting": PromptTemplate(
                input_variables=["question", "cdp", "context"],
                template="""
                You are an expert CDP support engineer for {cdp}.
                
                A user has reported an issue or needs troubleshooting help:
                {question}
                
                Based on the documentation, here is the relevant information:
                {context}
                
                Please provide a comprehensive troubleshooting guide that includes:
                1. Potential causes of the issue
                2. Step-by-step diagnostic process
                3. Resolution steps for each potential cause
                4. Verification steps to confirm the fix worked
                """
            ),
            "best_practices": PromptTemplate(
                input_variables=["question", "cdp", "context"],
                template="""
                You are an expert CDP consultant for {cdp}.
                
                A user has asked about best practices:
                {question}
                
                Based on the documentation, here is the relevant information:
                {context}
                
                Please provide comprehensive best practices that include:
                1. Industry-standard approaches
                2. Specific recommendations for {cdp}
                3. Performance optimization tips
                4. Security considerations
                5. Common pitfalls to avoid
                """
            ),
            "migration": PromptTemplate(
                input_variables=["question", "cdp", "context", "source_cdp"],
                template="""
                You are an expert CDP migration specialist.
                
                A user has asked about migrating to/from {cdp}:
                {question}
                
                They appear to be interested in migration {source_cdp} to/from {cdp}.
                
                Based on the documentation, here is the relevant information:
                {context}
                
                Please provide a comprehensive migration guide that includes:
                1. Pre-migration planning and assessment
                2. Data mapping considerations
                3. Step-by-step migration process
                4. Post-migration validation
                5. Common challenges and how to address them
                """
            )
        }
        
        # Create LLM chains for each advanced question type
        self.advanced_chains = {
            qtype: LLMChain(llm=self.llm, prompt=prompt) 
            for qtype, prompt in self.advanced_prompts.items()
        }
    
    def identify_question_type(self, question):
        """Identify the type of advanced question."""
        question_lower = question.lower()
        
        for qtype, patterns in self.advanced_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return qtype
        
        return None
    
    def extract_source_cdp(self, question, target_cdp):
        """Extract the source CDP for migration questions."""
        question_lower = question.lower()
        cdps = ["segment", "mparticle", "lytics", "zeotap"]
        
        for cdp in cdps:
            if cdp in question_lower and cdp != target_cdp:
                return cdp
        
        return "another CDP"
    
    def handle_advanced_question(self, question, cdp):
        """Handle advanced questions about a specific CDP."""
        # Identify the type of advanced question
        question_type = self.identify_question_type(question)
        
        if not question_type:
            return None  # Not an advanced question we can handle
        
        # Retrieve relevant documents
        docs = self.vector_db.similarity_search(
            question,
            k=5,
            filter={"cdp": cdp}
        )
        
        # Combine document content
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # For migration questions, try to identify source/target CDPs
        if question_type == "migration":
            source_cdp = self.extract_source_cdp(question, cdp)
            
            # Generate response
            response = self.advanced_chains[question_type].run(
                question=question,
                cdp=cdp,
                context=context,
                source_cdp=source_cdp
            )
        else:
            # Generate response for other advanced question types
            response = self.advanced_chains[question_type].run(
                question=question,
                cdp=cdp,
                context=context
            )
        
        return response
