from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_currency(value):
    """Clean currency strings by removing non-numeric characters except decimal point."""
    if pd.isna(value) or value is None:
        return 0.0
    if isinstance(value, str):
        # Remove currency symbols, commas, and extra spaces; replace comma with decimal point
        cleaned = re.sub(r'[^\d,.]', '', value.strip()).replace(',', '.')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    return float(value)

def clean_category(value):
    """Clean category strings by normalizing case and removing extra spaces."""
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip().lower()

@app.post("/analyze")
async def analyze_expenses(file: UploadFile = File(...)):
    # Verify file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV file with semicolon delimiter
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')), sep=';', skipinitialspace=True)

        # Normalize column names (remove spaces, convert to lowercase)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Identify amount and category columns
        amount_col = 'amount'  # Based on provided CSV
        category_col = 'category'  # Based on provided CSV

        if amount_col not in df.columns or category_col not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'amount' and 'category' columns")

        # Clean data
        df[amount_col] = df[amount_col].apply(clean_currency)
        df[category_col] = df[category_col].apply(clean_category)

        # Calculate total for "Food" category
        total_food = df[df[category_col].str.contains('food', case=False, na=False)][amount_col].sum()

        return {
            "answer": round(total_food, 2),
            "email": "example@domain.com",  # Replace with your actual email
            "exam": "tds-2025-05-roe"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")