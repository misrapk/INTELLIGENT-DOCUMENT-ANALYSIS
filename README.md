# Intelligent Document Analysis System

## About

This project leverages AI to analyze PDF business documents intelligently. It extracts text, performs summarization, identifies key entities, and generates business insights using the Perplexity AI API.

---

## Features

- PDF/document parsing and text extraction using `pdfplumber`
- Integration with Perplexity AI for document summarization and insights
- Named Entity Recognition for business entities
- Streamlit-based interactive web interface for easy user interaction
- Secure API key management via environment variables
- Modular, extensible architecture for future enhancements

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Perplexity AI API key (sign up at [Perplexity](https://www.perplexity.ai))

### Installation

1. Clone the repository:

git clone https://github.com/misrapk/INTELLIGENT-DOCUMENT-ANALYSIS.git
cd INTELLIGENT-DOCUMENT-ANALYSIS

text

2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate

text

3. Install dependencies:

pip install -r requirements.txt

text

4. Create a `.env` file in the root folder with your API key:

PERPLEXITY_API_KEY=your_perplexity_api_key_here

text

---

## Usage

To run the Streamlit app:

streamlit run frontend/mainApp.py

text

The app will open in your browser at `http://localhost:8501`. Upload a PDF document and get AI-generated summaries and insights.

---

## Project Structure

intelligent-doc-analysis/
├── app/
│ ├── document_processor.py # PDF text extraction
│ ├── perplexity_ai.py # Perplexity API integration
│ ├── ai_workflow.py # Summarization and insights logic
│ └── main.py # Backend logic (optional)
├── frontend/
│ └── mainApp.py # Streamlit web interface
├── data/
│ └── uploads/ # Upload documents here
├── .env # API keys (not committed to GitHub)
├── requirements.txt # Python dependencies
├── README.md # Project overview and instructions

text

---

## Contributing

Contributions are welcome! Please fork the repo and submit pull requests.

---

## License

This project is licensed under the MIT License.

---

## Contact

Created by [misrapk](https://github.com/misrapk).  
For questions or help, open an issue or contact via GitHub.