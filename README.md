# COE Round Robin Python Project

[![Azure DevOps Repo](https://img.shields.io/badge/Azure%20DevOps-Repo-blue?logo=azuredevops)](https://dev.azure.com/ANS-Profsvc/CoE%20-%20Data%20-%20Internal/_git/coe-round-robin)

This project provides tools and scripts for working with customer and resource data, including data processing and analysis. The codebase is organized for clarity and ease of use, with a focus on reproducibility and testability.

## Project Structure

```
coe-round-robin/
├── data/
│   ├── Data CoE Team & Customers.xlsx
│   └── dcoe_standup_sprint_to_psa_v3_20250519.xlsx
├── src/
│   └── app.py
├── test/
│   └── test_app.py
├── requirements.txt
├── pyproject.toml
├── .env.template
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8 or higher (Python 3.11 recommended)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://dev.azure.com/ANS-Profsvc/CoE%20-%20Data%20-%20Internal/_git/coe-round-robin
   git lfs install # if using Git LFS (optional)
   cd coe-round-robin
   ```
2. **Create a virtual environment (recommended):**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. **Install dependencies:**
   - Using `pyproject.toml` (recommended):
     ```sh
     pip install .
     ```
   - For development (with optional dev dependencies):
     ```sh
     pip install -e .[dev]
     ```
   - Alternatively, using `requirements.txt`:
     ```sh
     pip install -r requirements.txt
     ```
4. **Set up environment variables:**
   - Copy the `.env.template` file to `.env` and update the values as needed:
     ```sh
     cp .env.template .env
     ```
   - The following environment variables are available:
     - `MAX_SAMPLES` (default: 200)
     - `HOURS_DIVISOR` (default: 15)
     - `RANDOM_SEED` (set as needed)

## Usage

- Main application scripts are in the `src/` directory. For example, to run the main app:
  ```sh
  python src/app.py
  ```
- Data files are located in the `data/` directory.

## Project Configuration

- All project metadata and dependencies are specified in [`pyproject.toml`](./pyproject.toml).
- The project uses [PEP 517/518](https://www.python.org/dev/peps/pep-0517/) standards for build and dependency management.

## Testing

- Tests are located in the `test/` directory.
- This project uses `pytest` for testing. To run all tests:
  ```sh
  pytest
  ```
- Test configuration is set in `.vscode/settings.json` (pytest enabled, unittest disabled).

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

## License

This project is licensed under the Apache License 2.0.

## Additional Notes

- Ensure your virtual environment is activated before running or testing the code.
- Update `pyproject.toml` if you add new dependencies. You may also update `requirements.txt` for compatibility.
- For any issues, please open an issue in the [Azure DevOps repository](https://dev.azure.com/ANS-Profsvc/CoE%20-%20Data%20-%20Internal/_git/coe-round-robin).
