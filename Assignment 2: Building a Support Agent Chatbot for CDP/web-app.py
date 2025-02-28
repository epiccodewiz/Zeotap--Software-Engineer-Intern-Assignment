from flask import Flask, request, jsonify, render_template
import os
from question_processor import QuestionProcessor
from response_generator import ResponseGenerator
from document_processor import DocumentProcessor

app = Flask(__name__)

# Initialize components
processor = DocumentProcessor()
vector_db = processor.load_vector_database()
question_processor = QuestionProcessor(vector_db)
response_generator = ResponseGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_question = data.get('question', '')
    
    # Process the question
    question_info = question_processor.classify_question(user_question)
    
    # Retrieve relevant documents
    if question_info["type"] != "unrelated":
        retrieved_docs = question_processor.retrieve_documents(question_info)
    else:
        retrieved_docs = None
    
    # Generate response
    response = response_generator.generate_response(question_info, retrieved_docs)
    
    # Return the response
    return jsonify({
        'response': response,
        'question_type': question_info["type"],
        'cdp': question_info.get("cdp", None) or question_info.get("cdps", None)
    })

if __name__ == '__main__':
    app.run(debug=True)
