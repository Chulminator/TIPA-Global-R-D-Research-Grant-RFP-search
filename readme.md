🔍 Global R&D RFP Integrated Search Engine
    This platform is an automated solution designed to manage and explore over 600+ Technology Proposals (RFPs) from global research institutes. It transforms unstructured PDF data into a searchable web-based dashboard.

🚀 Workflow Pipeline
    To ensure data accuracy and system performance, the project follows a structured 4-step execution process:

    step1 rfp-to-csv.py:

        Scans the raw PDF directory.

        Extracts metadata (PI, Title, Technology Fields) using Regex and PyMuPDF.

        Generates the initial rfp_summary.csv.

    step2 Manual Edit (rfp_summary-manual-edit.csv):

        Human-in-the-loop stage to refine and verify extracted data.

        Ensures high data quality for strategic technical fields.

    step3 csv_to_db_loader.py:

        Loads the refined CSV data into a lightweight SQLite database (projects.db).

        Creates indexes for high-speed searching.

    step4 main.py:

        The Streamlit frontend that serves the final search engine.

        Connects to the DB to provide real-time filtering and PDF download links.

✨ Key Features
    Automated ETL: Converts hundreds of complex PDFs into structured data in seconds.
    Multi-Criteria Search: Search by institution, project title, PI name, or technical keywords.
    Optimized UI: Responsive data tables with auto-sizing columns and single-row detail views.
    Direct Access: Integrated download buttons for full RFP packages from global partners.

🛠 Tech Stack
    Language: Python 3.x
    Data Processing: Pandas, PyMuPDF (fitz)
    Database: SQLite3
    Web Framework: Streamlit

📂 Project Structure

    ├── rfp-to-csv.py           # Step 1: PDF to CSV Extractor
    ├── csv_to_db_loader.py     # Step 3: CSV to SQLite Loader
    ├── main.py                 # Step 4: Streamlit Web Application
    ├── projects.db             # Final Indexed Database
    ├── requirements.txt        # Deployment Dependencies
    └── RFP목록/                 # Source PDF Repository

⚙️ Setup & Deployment
    Install Dependencies

    pip install -r requirements.txt
    Execute Pipeline (If updating data)

    Bash
    python rfp-to-csv.py
    # Edit the CSV manually if needed
    python csv_to_db_loader.py
    streamlit run main.py