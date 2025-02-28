# Example questions for testing the CDP chatbot

basic_questions = [
    # Segment questions
    "How do I set up a new source in Segment?",
    "How can I track events in Segment?",
    "What are the steps to create a destination in Segment?",
    
    # mParticle questions
    "How can I create a user profile in mParticle?",
    "How do I set up data inputs in mParticle?",
    "What's the process for configuring outputs in mParticle?",
    
    # Lytics questions
    "How do I build an audience segment in Lytics?",
    "How can I set up data collection in Lytics?",
    "What steps are needed to create campaigns in Lytics?",
    
    # Zeotap questions
    "How can I integrate my data with Zeotap?",
    "How do I set up audiences in Zeotap?",
    "What's the process for identity resolution in Zeotap?"
]

comparison_questions = [
    "How does Segment's audience creation process compare to Lytics'?",
    "What are the differences between mParticle and Zeotap for data collection?",
    "Which CDP has better privacy compliance features: Segment or mParticle?",
    "Can you compare the integration capabilities of all four CDPs?",
    "How do user profiles differ between Lytics and Zeotap?"
]

advanced_questions = [
    # Implementation questions
    "How do I implement advanced cross-device tracking in Segment?",
    "What's the best way to set up multi-environment configurations in mParticle?",
    "How can I implement custom identity resolution in Lytics?",
    "What steps are needed for enterprise-level implementation of Zeotap?",
    
    # Troubleshooting questions
    "Why isn't my Segment tracking working on Safari browsers?",
    "How do I debug data inconsistencies in mParticle user profiles?",
    "What should I do if my audience segments in Lytics aren't updating?",
    "How can I troubleshoot integration issues between Zeotap and my DMP?",
    
    # Best practices
    "What are the best practices for implementing Segment in a high-traffic website?",
    "What's the recommended approach for handling sensitive data in mParticle?",
    "What are security best practices for Lytics implementation?",
    "What are the optimal settings for real-time data processing in Zeotap?",
    
    # Migration questions
    "How do I migrate from Adobe Analytics to Segment?",
    "What's the process for transitioning from Segment to mParticle?",
    "How can I move my audience segments from Lytics to Zeotap?",
    "What steps should I take to migrate from a custom CDP solution to Segment?"
]

edge_case_questions = [
    # Extremely long questions
    "I'm trying to figure out how to set up a new data source in Segment that can track user interactions across multiple platforms including our web application, mobile apps for both iOS and Android, and our internal CRM system, while ensuring that all of the data is properly unified into a single user profile and then appropriately segmented based on behavior patterns so that we can target specific user cohorts with personalized messaging through our various marketing channels including email, push notifications, SMS, and in-app messaging, and I also need to make sure that this implementation is compliant with GDPR, CCPA, and other privacy regulations. Can you provide a step-by-step guide on how to accomplish this?",
    
    # Ambiguous questions
    "How do I set up tracking?",
    "What's the best way to create segments?",
    "How do profiles work?",
    
    # Non-CDP questions
    "What's the weather like today?",
    "Can you recommend a good movie to watch?",
    "How do I bake a chocolate cake?",
    
    # Mixed questions
    "How do I set up Segment and also what's the capital of France?",
    "Can you tell me about audience creation in mParticle and also who won the last Super Bowl?"
]

import time
from document_processor import DocumentProcessor
from question_processor import QuestionProcessor
from response_generator import ResponseGenerator
def run_test_suite():
    # Load components
    processor = DocumentProcessor()
    vector_db = processor.load_vector_database()
    question_processor = QuestionProcessor(vector_db)
    response_generator = ResponseGenerator()
    
    def test_question(question):
        print(f"\nTesting question: {question}")
        start_time = time.time()
        
        # Process question
        question_info = question_processor.classify_question(question)
        print(f"Question classified as: {question_info['type']}")
        
        # Retrieve documents
        if question_info["type"] != "unrelated":
            retrieved_docs = question_processor.retrieve_documents(question_info)
            doc_count = len(retrieved_docs)
        else:
            retrieved_docs = None
            doc_count = 0
        
        # Generate response
        response = response_generator.generate_response(question_info, retrieved_docs)
        
        # Print info
        end_time = time.time()
        print(f"Retrieved {doc_count} documents")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Response preview: {response[:100]}...")
        
    # Test different categories
    print("==== TESTING BASIC QUESTIONS ====")
    for q in basic_questions[:3]:  # Test a few from each category
        test_question(q)
        
    print("\n==== TESTING COMPARISON QUESTIONS ====")
    for q in comparison_questions[:2]:
        test_question(q)
        
    print("\n==== TESTING ADVANCED QUESTIONS ====")
    for q in advanced_questions[:2]:
        test_question(q)
        
    print("\n==== TESTING EDGE CASES ====")
    for q in edge_case_questions[:3]:
        test_question(q)

if __name__ == "__main__":
    run_test_suite()
