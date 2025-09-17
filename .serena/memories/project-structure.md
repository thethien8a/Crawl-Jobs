# Project Structure - CrawlJob (Updated 2025-09-15)

## 📁 **Root Directory Structure**

```
D:\Practice\Scrapy\CrawlJob\
├── 📄 README.md                    # Comprehensive documentation
├── 📄 requirements.txt             # Python dependencies
│
├── 📁 CrawlJob/                    # Main Scrapy project
├── 📁 api/                         # FastAPI backend
├── 📁 great_expectations/          # Great Expectations Data Context (Auto-managed)
│
├── 📁 validation/                  # (NEW) Custom programmatic management of GE
│   ├── 📁 GX_CLASS/
│   │   ├── 📄 __init__.py
│   │   └── 📄 gx_class.py          # Core class encapsulating GE API interactions
│   ├── 📄 __init__.py
│   ├── 📄 checkpoints_definition.py# Script for defining GE components using GXClass
│   └── 📄 run_checkpoint.py        # Script for executing a defined Checkpoint
│
└── ... (other project folders like web/, logs/, etc.)
```

## 🆕 **New Components (2025-09-15) - Data Quality Integration**

### **Programmatic Validation (`validation/` folder)**
- **Purpose**: This directory houses a custom, object-oriented framework for interacting with Great Expectations programmatically, providing an alternative to the standard CLI workflow.
- **`GX_CLASS/gx_class.py`**: A powerful wrapper class that contains methods to create and manage datasources, assets, expectation suites, and checkpoints. This is the core library for GE automation in this project.
- **`checkpoints_definition.py`**: The entry point script for setting up and defining GE components. It instantiates `GXClass` and uses its methods to configure the validation environment.
- **`run_checkpoint.py`**: The entry point script for execution. It's designed to be called by an orchestrator (like Airflow) to trigger a specific, pre-defined checkpoint.
- **Adherence to Single Responsibility**: This structure clearly separates the reusable library (`GX_CLASS`), the setup/definition logic (`checkpoints_definition`), and the execution logic (`run_checkpoint`).
