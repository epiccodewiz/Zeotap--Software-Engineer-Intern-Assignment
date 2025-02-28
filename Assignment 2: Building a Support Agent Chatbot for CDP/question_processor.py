from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

class QuestionProcessor:
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.cdp_names = ["segment", "mparticle", "lytics", "zeotap"]
        
        # For classifying question types
        self.how_to_patterns = [
            r"how (do|can|to|would|should) (i|we|you)",
            r"what (is|are) the (step|steps|way|ways|method|methods|process|approach)",
            r"guide (for|to)",
            r"tutorial (for|on)",
            r"(steps|instructions) (for|to)",
        ]
        
        self.comparison_patterns = [
            r"(compare|comparison|versus|vs|difference|different|better)",
            r"(which|what) (is|are) (better|worse|faster|easier|more|less)",
        ]
        
        # Sample how-to questions for each CDP
        self.sample_questions = {
            "segment": [
                "How do I set up a source in Segment?",
                "How to create a destination in Segment?",
                "Setting up tracking in Segment",
                "Segment implementation guide",
            ],
            "mparticle": [
                "How to create a user profile in mParticle?",
                "Setting up data inputs in mParticle",
                "mParticle event tracking setup",
                "How do I configure outputs in mParticle?",
            ],
            "lytics": [
                "How do I build an audience segment in Lytics?",
                "Setting up data collection in Lytics",
                "Lytics integration guide",
                "How to create campaigns in Lytics?",
            ],
            "zeotap": [
                "How can I integrate my data with Zeotap?",
                "Setting up audiences in Zeotap",
                "Zeotap implementation steps",
                "How do I use Zeotap for identity resolution?",
            ],
        }
        
        # Create vectorizer and fit on sample questions
        all_samples = []
        for cdp, questions in self.sample_questions.items():
            all_samples.extend(questions)
        
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(all_samples)
        
        # Create vectors for sample questions
        self.cdp_vectors = {}
        for cdp, questions in self.sample_questions.items():
            self.cdp_vectors[cdp] = self.vectorizer.transform(questions)
    
    def is_how_to_question(self, question):
        """Determine if the question is a how-to question."""
        question_lower = question.lower()
        for pattern in self.how_to_patterns:
            if re.search(pattern, question_lower):
                return True
        return False
    
    def is_comparison_question(self, question):
        """Determine if the question is asking for a comparison between CDPs."""
        question_lower = question.lower()
        
        # Check if it mentions multiple CDPs
        cdp_count = sum(1 for cdp in self.cdp_names if cdp in question_lower)
        
        # Check for comparison patterns
        has_comparison_pattern = any(re.search(pattern, question_lower) for pattern in self.comparison_patterns)
        
        return (cdp_count >= 2 or has_comparison_pattern)
    
    def identify_cdp(self, question):
        """Identify which CDP the question is about."""
        # First, explicit mention check
        question_lower = question.lower()
        for cdp in self.cdp_names:
            if cdp in question_lower:
                return cdp
        
        # If no explicit mention, use vectorizer for similarity
        question_vector = self.vectorizer.transform([question])
        
        max_similarity = -1
        best_cdp = None
        
        for cdp, vectors in self.cdp_vectors.items():
            similarities = cosine_similarity(question_vector, vectors)
            max_cdp_similarity = np.max(similarities)
            
            if max_cdp_similarity > max_similarity:
                max_similarity = max_cdp_similarity
                best_cdp = cdp
        
        # Only return a CDP if we have reasonable confidence
        if max_similarity > 0.3:
            return best_cdp
        return None
    
    def classify_question(self, question):
        """Classify the question type and extract relevant information."""
        if self.is_comparison_question(question):
            # Identify which CDPs are being compared
            mentioned_cdps = [cdp for cdp in self.cdp_names if cdp in question.lower()]
            
            if len(mentioned_cdps) < 2:
                # If not explicitly mentioned, assume all
                mentioned_cdps = self.cdp_names
                
            return {
                "type": "comparison",
                "cdps": mentioned_cdps,
                "question": question
            }
        
        elif self.is_how_to_question(question):
            cdp = self.identify_cdp(question)
            
            if cdp:
                return {
                    "type": "how-to",
                    "cdp": cdp,
                    "question": question
                }
            else:
                # How-to question but can't determine which CDP
                return {
                    "type": "ambiguous",
                    "question": question
                }
        
        else:
            # Not a CDP-related question
            return {
                "type": "unrelated",
                "question": question
            }
    
    def retrieve_documents(self, question_info, top_k=5):
        """Retrieve relevant documents based on the question classification."""
        if question_info["type"] == "how-to":
            # Search in the vector database with metadata filter for specific CDP
            docs = self.vector_db.similarity_search(
                question_info["question"],
                k=top_k,
                filter={"cdp": question_info["cdp"]}
            )
            return docs
            
        elif question_info["type"] == "comparison":
            # For comparison questions, get documents for each CDP
            all_docs = []
            for cdp in question_info["cdps"]:
                docs = self.vector_db.similarity_search(
                    question_info["question"],
                    k=3,  # Fewer per CDP since we're getting multiple
                    filter={"cdp": cdp}
                )
                all_docs.extend(docs)
            return all_docs
            
        elif question_info["type"] == "ambiguous":
            # Search across all CDPs
            docs = self.vector_db.similarity_search(
                question_info["question"],
                k=top_k
            )
            return docs
            
        else:  # unrelated
            return []
