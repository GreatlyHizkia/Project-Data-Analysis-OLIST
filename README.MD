# Olist E-Commerce Data Analysis Dashboard 📊

## Project Structure
- `dashboard/`: Contains the main dashboard script and the processed dataset.
- `data/`: Contains the raw CSV files used for analysis.
- `notebook.ipynb`: The notebook where data cleaning and exploratory data analysis (EDA) were performed.
- `requirements.txt`: List of Python libraries required to run the project.
- `url.txt`: Link to the live dashboard on Streamlit Cloud.

## Setup Environment - Anaconda
To run this project on your local machine using Anaconda, follow these steps:

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Run streamlit app
```bash
streamlit run dashboard/dashboard.py
```