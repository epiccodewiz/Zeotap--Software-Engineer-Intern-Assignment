# CDP Chatbot

A specialized chatbot designed to answer questions about four major Customer Data Platforms (CDPs): Segment, mParticle, Lytics, and Zeotap. The chatbot uses natural language processing and vector search to provide accurate, targeted responses to user questions about these platforms.

## Overview

This chatbot can:
- Answer "how-to" questions for specific CDPs
- Compare features across multiple CDPs
- Handle advanced implementation, troubleshooting, and migration questions
- Process questions with appropriate context based on question type

## Technology Stack

- **Python 3.11**: Core programming language
- **LangChain**: Framework for building applications with Large Language Models
- **HuggingFace**: Model hosting and inference
  - Using `google/flan-t5-xl` for response generation
  - Using `sentence-transformers/all-mpnet-base-v2` for embeddings
- **FAISS**: Vector database for efficient similarity search
- **Flask**: Web application framework for the UI
- **BeautifulSoup4**: Web scraping library for documentation collection
- **scikit-learn**: For TF-IDF vectorization and classification

## Project Structure

- `document_processor.py`: Handles loading, processing, and embedding documents
- `question_processor.py`: Classifies questions and retrieves relevant documents
- `response_generator.py`: Generates responses using LLM chains
- `advanced_question_handler.py`: Specialized handling for complex questions
- `comparison_engine.py`: Processes questions comparing multiple CDPs
- `scrape.py`: Scrapes documentation from CDP websites
- `web-app.py`: Flask web application for the chatbot interface
- `example_questions.py`: Sample questions for testing

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone 
   cd cdp-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for API access:
   ```bash
   # On Windows
   set HUGGINGFACEHUB_API_TOKEN=your_token_here
   # On macOS/Linux
   export HUGGINGFACEHUB_API_TOKEN=your_token_here
   ```

### Data Collection

1. Run the scraper to collect documentation:
   ```bash
   python scrape.py
   ```
   This will create folders with documentation from each CDP.

2. Process the documents to create the vector database:
   ```bash
   python -c "from document_processor import DocumentProcessor; DocumentProcessor().process_directory('segment_docs', 'segment')"
   ```
   Repeat for each CDP folder (`segment_docs`, `mparticle_docs`, `lytics_docs`, `zeotap_docs`).

### Running the Application

1. Start the Flask web application:
   ```bash
   python web-app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Start asking questions about the supported CDPs!

## How It Works

### 1. Document Processing Pipeline

```
Documentation → Web Scraping → Text Chunking → Embeddings → Vector Database
```

The system:
- Scrapes documentation from official CDP websites
- Splits documents into manageable chunks
- Creates embeddings using Hugging Face's sentence transformer
- Stores embeddings in a FAISS vector database for efficient retrieval

### 2. Question Processing

```
User Question → Classification → CDP Identification → Document Retrieval
```

The system:
- Determines if a question is a how-to, comparison, or advanced question
- Identifies which CDP(s) the question is about
- Retrieves the most relevant documentation chunks

### 3. Response Generation

```
Question Type + Retrieved Documents → LLM Chain → Structured Response
```

The system:
- Uses specialized prompt templates based on question type
- Passes relevant context from retrieved documents
- Generates a tailored response using the LLM

## Question Types Handled

1. **How-To Questions**: 
   - "How do I set up a new source in Segment?"
   - "How can I track events in mParticle?"

2. **Comparison Questions**:
   - "How does Segment's audience creation compare to Lytics?"
   - "Which CDP has better privacy compliance: Segment or mParticle?"
