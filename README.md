# AARVIK-s-Repo
# AARVIK - AI Document Assistant

![AARVIK Logo](https://via.placeholder.com/150?text=AARVIK) <!-- Replace with actual logo URL if available -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-yellow.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-orange.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)

Welcome to **AARVIK** (AI-powered Answering with Retrieval, Vectorization, and Interactive Knowledgebase), an innovative application that allows users to upload PDF documents and interact with them using AI-driven question-answering capabilities. Built with Streamlit and FastAPI, AARVIK leverages advanced natural language processing and vector-based retrieval to provide context-aware responses.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Current Status](#current-status)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Multi-document Support**: Upload and manage multiple PDFs within separate sessions.
- **Smart Retrieval**: Utilizes vector-based search (powered by FAISS) for efficient document analysis.
- **AI-powered Answers**: Integrates Google Generative AI and LangChain for context-aware question-answering.
- **Session Management**: Create, select, and delete sessions to organize your work.
- **Chat History**: Track all questions and answers with timestamps.
- **Modern Interface**: Clean, intuitive UI with dark mode compatibility.

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- An active internet connection (for API and dependency installation)

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/aarvik.git
   cd aarvik

Set Up a Virtual Environment
bashpython -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Install Dependencies

Install the required packages from requirements.txt. Note: There is a known dependency conflict (detailed below) that needs resolution.
Run:
bashpip install -r requirements.txt

Dependency Conflict Resolution: A conflict exists between google-generativeai==0.8.5 (requiring google-ai-generativelanguage==0.6.15) and langchain-google-genai==2.1.7 (requiring google-ai-generativelanguage>=0.6.18,<0.7.0). To resolve:

Edit requirements.txt to use google-ai-generativelanguage>=0.6.18,<0.7.0 or update google-generativeai to a version compatible with 0.6.18 (e.g., 0.8.6 or later).
Re-run pip install -r requirements.txt.
If issues persist, consider loosening version constraints or installing compatible versions manually (e.g., downgrade langchain-google-genai to 2.0.0).




Configure Environment Variables

Create a .env file in the project root with the following:
textMONGO_URL=your_mongodb_atlas_url
DB_NAME=your_database_name
GOOGLE_AI_API_KEY=your_google_api_key

Replace placeholders with your actual credentials.


Run the Application

Start the FastAPI backend:
bashuvicorn server:app --reload --port 8000

Start the Streamlit frontend:
bashstreamlit run app.py --server.port 8501

Open http://localhost:8501 in your browser.



Usage

Create a Session: Click "Create New Session" in the sidebar to generate a unique session.
Upload Documents: Use the "Document Upload" section to upload PDF files.
Ask Questions: Enter a question in the "Chat with Your Documents" section and click "Ask Question" to get AI-generated answers.
Manage Sessions: Select or delete sessions via the sidebar to organize your work.

Project Structure
textaarvik/
├── .venv/              # Virtual environment
├── app.py             # Streamlit frontend
├── server.py          # FastAPI backend (assumed)
├── requirements.txt   # Dependency list
├── .env               # Environment variables
└── README.md          # This file
Dependencies

Frontend: streamlit==1.31.0, requests==2.32.4
Backend: fastapi, uvicorn
AI/ML: google-generativeai==0.8.5, langchain==0.3.26, langchain-google-genai==2.1.7, faiss-cpu==1.8.0, PyPDF2==3.0.0
Database: pymongo==4.5.0, motor==3.3.1
Others: numpy==1.26.4, pandas==2.3.1, tqdm==4.67.1

See requirements.txt for the full list. Note the dependency conflict mentioned above.
Current Status

As of October 26, 2025: The project is in active development. The Streamlit frontend is functional with a polished UI, and the FastAPI backend structure is in place. However, a dependency conflict prevents the full application from running end-to-end.
Known Issues:

Dependency conflict between google-generativeai and langchain-google-genai requires resolution.
Backend integration and AI model testing are pending full dependency setup.


Next Steps: Resolve dependencies, test API endpoints, and validate AI functionality with sample PDFs.

Contributing
We welcome contributions to improve AARVIK! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes and commit them (git commit -m "Description of changes").
Push to the branch (git push origin feature-branch).
Open a Pull Request with a clear description of your changes.

Please ensure your code follows PEP 8 guidelines and includes tests where applicable.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact

Author: [Your Name]
Email: [your.email@example.com]
GitHub: [https://github.com/your-username]

Feel free to open an issue or reach out for support or collaboration!
