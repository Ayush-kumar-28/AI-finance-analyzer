# Finance Tracker — Complete Project Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [ML Model — Training & Details](#4-ml-model--training--details)
5. [Step-by-Step: What Happens When a User Uploads a Bank Statement](#5-step-by-step-what-happens-when-a-user-uploads-a-bank-statement)
   - Step 1: File Upload (Frontend)
   - Step 2: Backend Receives the File
   - Step 3: ML Service — Data Cleaning Pipeline
   - Step 4: Database Storage
   - Step 5: NLP Text Processing
   - Step 6: ML Classification
   - Step 7: Financial Summary Calculation
   - Step 8: Online Learning
   - Step 9: Response Sent to Frontend
   - Step 10: Dashboard Rendered
6. [Transaction Classification System](#6-transaction-classification-system)
7. [Investment Advice Engine](#7-investment-advice-engine)
8. [Online Learning System](#8-online-learning-system)
9. [Database Schema](#9-database-schema)
10. [API Endpoints Reference](#10-api-endpoints-reference)
11. [Supported File Formats](#11-supported-file-formats)
12. [Categories Reference](#12-categories-reference)

---

## 1. Project Overview

Finance Tracker is a full-stack AI-powered web application that allows users to upload their bank statements and automatically get a complete financial analysis. The system reads the raw bank statement, cleans the data, classifies every transaction into a spending category using Machine Learning, calculates income vs expense totals, and provides personalized investment advice — all in under 2 seconds.

**Core capabilities:**
- Accepts CSV, Excel (.xlsx/.xls), and PDF bank statements
- Automatically detects column formats from any bank
- Classifies transactions into 14 categories using a hybrid Rule + ML engine
- Separates credit (income) from debit (expense) transactions
- Displays interactive charts and category breakdowns
- Provides real-time investment recommendations
- Learns from every upload to improve accuracy over time

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    React.js Frontend                        │
│         (FileUpload → Dashboard → InvestmentAdvice)         │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP (multipart/form-data)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Node.js Backend                           │
│                   Express.js Server                         │
│                     Port: 5000                              │
│   - Receives file upload                                    │
│   - Validates file type and size                            │
│   - Forwards to ML Service via axios                        │
│   - Proxies all API calls                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP (multipart/form-data)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Python ML Service                         │
│                   FastAPI Server                            │
│                     Port: 8000                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           7-Step Processing Pipeline                │   │
│  │                                                     │   │
│  │  1. Data Cleaning (Pandas)                          │   │
│  │  2. Store in SQLite/PostgreSQL                      │   │
│  │  3. Retrieve from Database                          │   │
│  │  4. NLP Text Processing                             │   │
│  │  5. ML Classification (TF-IDF + LinearSVC)          │   │
│  │  6. Financial Summary Calculation                   │   │
│  │  7. Online Learning (save for retraining)           │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database                               │
│              SQLite (default) / PostgreSQL                  │
│   Tables: transactions, uploaded_files,                     │
│            financial_summaries, category_breakdowns         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js | UI, charts, file upload |
| Charts | Recharts | Bar chart, Pie chart |
| File Drop | react-dropzone | Drag & drop file upload |
| HTTP Client | Axios | API calls from frontend |
| Backend | Node.js + Express.js | API gateway, file proxy |
| File Upload | Multer | Multipart file handling |
| ML Service | Python + FastAPI | Core ML processing |
| ML Model | scikit-learn LinearSVC | Transaction classification |
| Vectorizer | TF-IDF (scikit-learn) | Text feature extraction |
| Data Processing | Pandas + NumPy | Data cleaning and analysis |
| PDF Parsing | pdfplumber | Extract tables from PDF |
| Database ORM | SQLAlchemy | Database abstraction |
| Database | SQLite / PostgreSQL | Transaction storage |
| Deployment | Render.yaml | Cloud deployment config |

---

## 4. ML Model — Training & Details

### Model Type
**Linear Support Vector Machine (LinearSVC)**

LinearSVC is a linear classifier that finds the optimal hyperplane to separate transaction categories. It is chosen because:
- Very fast for text classification (milliseconds per prediction)
- Works well with high-dimensional sparse TF-IDF features
- Handles multi-class classification natively
- Performs well even with limited training data

### Text Vectorization
**TF-IDF (Term Frequency — Inverse Document Frequency)**

TF-IDF converts raw transaction text into numerical feature vectors. Each word (and word combination) gets a score based on how often it appears in a transaction vs how common it is across all transactions.

**TF-IDF Configuration:**
```
max_features   = 150        (top 150 most informative words/phrases)
ngram_range    = (1, 3)     (unigrams, bigrams, trigrams)
min_df         = 1          (include rare terms)
max_df         = 0.95       (ignore terms in >95% of documents)
sublinear_tf   = True       (log scaling for term frequency)
strip_accents  = 'unicode'  (normalize accented characters)
lowercase      = True       (case normalization)
```

### Training Process (6 Steps)

**Step 1 — Load Dataset**
- File: `training/dataset.csv`
- Contains labeled transaction descriptions with categories
- Example: `"ZOMATO ORDER 12345"` → `"Food"`

**Step 2 — Clean Text**
- Apply NLP cleaning to all descriptions (see Section 5, Step 5 for details)
- Example: `"UPI/ZOMATO/REF123456/12-01-2024"` → `"zomato order"`

**Step 3 — Train/Test Split**
- 80% training data, 20% test data
- `stratify=True` ensures each category is proportionally represented in both splits
- `random_state=42` for reproducibility

**Step 4 — TF-IDF Vectorization**
- Fit vectorizer on training data only (to prevent data leakage)
- Transform both train and test sets

**Step 5 — Train LinearSVC**
```
C              = 1.0        (regularization — balance between margin and misclassification)
class_weight   = 'balanced' (handles class imbalance automatically)
max_iter       = 2000       (maximum optimization iterations)
dual           = False      (faster when samples > features)
random_state   = 42
```

**Step 6 — Evaluate**
- Accuracy score on test set
- Full classification report (precision, recall, F1 per category)
- Confusion matrix to identify most confused category pairs
- Per-category accuracy breakdown

### Saved Model Files
```
app/models/svm_model.pkl      ← trained LinearSVC model
app/models/vectorizer.pkl     ← fitted TF-IDF vectorizer
```

Both are serialized with Python's `pickle` and loaded once at ML service startup.

---

## 5. Step-by-Step: What Happens When a User Uploads a Bank Statement

### Step 1 — File Upload (Frontend)

**File:** `frontend/src/components/FileUpload.js`

1. User drags and drops a file (or clicks to browse) onto the upload zone
2. `react-dropzone` validates the file on the client side:
   - Accepted formats: `.csv`, `.xlsx`, `.xls`, `.pdf`
   - Maximum size: 10 MB
3. If valid, `onFileUpload(file)` is called in `App.js`
4. `App.js` creates a `FormData` object and appends the file
5. Axios sends a `POST` request to `/api/analyze` with `Content-Type: multipart/form-data`
6. A loading spinner is shown while waiting for the response

---

### Step 2 — Backend Receives the File

**File:** `backend/server.js`

1. Express.js receives the `POST /api/analyze` request
2. **Multer** middleware handles the multipart upload:
   - Saves the file temporarily to `backend/uploads/` with a unique timestamped filename
   - Enforces 10 MB file size limit
   - Rejects files with invalid extensions
3. Backend creates a new `FormData` object and streams the saved file
4. Sends a `POST` request to the ML Service at `http://localhost:8000/analyze`
5. After the ML service responds, the temporary file is deleted from `uploads/`
6. The ML service response is forwarded directly back to the frontend

---

### Step 3 — ML Service: Data Cleaning Pipeline

**File:** `ml-service/data_cleaning_pipeline.py`

This is the most complex step. The pipeline handles 3 different file formats and 11 cleaning sub-steps.

#### 3a. Format Detection & Raw Extraction

The file extension determines which extractor runs:

**CSV files** (`_extract_csv`):
- `pd.read_csv()` loads the file into a DataFrame
- Passes to `_standardize_columns()`

**Excel files** (`_extract_excel`):
- `pd.read_excel()` loads the file
- Passes to `_standardize_columns()`

**PDF files** (`_extract_pdf`):
- `pdfplumber` opens the PDF
- For each page, tries **table extraction** first (structured tables)
- If no tables found, falls back to **text extraction** (unstructured text)
- Table parser (`_parse_pdf_table`) finds header row, locates description/debit/credit columns, and extracts rows
- Text parser (`_parse_pdf_text`) uses regex to find date patterns and ₹ amounts

#### 3b. Column Standardization (`_standardize_columns`)

The system uses **Adaptive Learning** to handle any bank's column naming:

1. Converts all column names to lowercase
2. Checks `cleaning_patterns.json` for previously learned column mappings
3. Tries to match columns to standard names: `description`, `amount`, `debit`, `credit`
4. Supports fuzzy matching (e.g. `"Transaction Details"` → `description`)
5. Learns new column name variations and saves them for future uploads

**Transaction type detection:**
- If file has separate `debit` and `credit` columns → sets `transaction_type = 'credit'` or `'debit'` based on which column has a value
- If file has a single `amount` column → defaults to `'debit'`, then scans description for credit keywords: `credit, credited, deposit, received, salary, income, refund, cashback, interest`

#### 3c. Advanced Cleaning Pipeline (11 Sub-Steps)

| Sub-Step | Operation | What It Does |
|---|---|---|
| 1 | Remove nulls | Drops rows where description or amount is missing |
| 2 | Remove suspicious duplicates | Keeps up to 2 identical transactions (legitimate), removes if >2 |
| 3 | Remove near-duplicates | Uses Jaccard similarity — removes if >90% similar text AND amount differs by <₹1 |
| 4 | Advanced description cleaning | Strips transaction IDs, dates, times, reference numbers, account numbers, currency symbols |
| 5 | Validate amounts | Converts to numeric, removes zero/negative, removes amounts >₹1 crore, rounds to 2 decimal places |
| 6 | Outlier detection | Calculates IQR bounds (3×IQR), flags outliers as warnings but keeps them (salary/rent are legitimate large amounts) |
| 7 | Validate descriptions | Removes descriptions shorter than 3 chars, longer than 500 chars, or containing only numbers/special characters |
| 8 | Remove test transactions | Removes rows with keywords: test, dummy, sample, example, xxx |
| 9 | Standardize formatting | Trims whitespace, normalizes multiple spaces |
| 10 | Ensure transaction_type | Fills any missing `transaction_type` by scanning description for credit keywords |
| 11 | Reset index | Resets DataFrame index after all removals |

#### 3d. Quality Scoring

After cleaning, a **Data Quality Score (0–100)** is calculated:
- Starts at 100
- Deducts points for data loss (if retention rate < 90%)
- Deducts 5 points per anomaly detected
- Deducts 3 points per warning
- Adds 5 bonus points if average description length > 20 characters

#### 3e. Pattern Detection

Scans all descriptions for common transaction patterns and counts them:
- UPI transactions
- NEFT transfers
- IMPS transfers
- ATM withdrawals
- Card payments

---

### Step 4 — Database Storage

**Files:** `ml-service/database.py`, `ml-service/db_manager.py`

1. A unique `file_id` (UUID) is generated for this upload
2. **SQLAlchemy ORM** stores data in 4 tables:

**`uploaded_files` table** — file metadata:
- filename, format, size
- original_rows, cleaned_rows, removed_rows
- retention_rate, quality_score, processing_time
- uploaded_at timestamp, processed flag

**`transactions` table** — one row per transaction:
- file_id (links to uploaded_files)
- description, amount
- transaction_type ('credit' or 'debit')
- category (NULL at this point — filled after ML classification)
- confidence (NULL at this point)

3. All transactions are bulk-inserted for performance
4. The `file_id` is returned for use in subsequent steps

---

### Step 5 — NLP Text Processing

**File:** `app/utils/text_cleaner.py`

Before ML classification, every transaction description goes through NLP cleaning:

| Operation | Example Input | Example Output |
|---|---|---|
| Lowercase | `"ZOMATO ORDER"` | `"zomato order"` |
| Remove URLs | `"pay.zomato.com/abc"` | `""` |
| Remove emails | `"noreply@hdfc.com"` | `""` |
| Remove dates | `"12/01/2024"` | `""` |
| Remove times | `"14:32:05"` | `""` |
| Remove ref numbers | `"REF123456789"` | `""` |
| Remove account numbers | `"XXXX4521"` | `""` |
| Remove currency amounts | `"₹1,500.00"` | `""` |
| Normalize bank keywords | `"NEFT"` | `"transfer"` |
| Remove special characters | `"zomato/order#1"` | `"zomato order"` |
| Remove stop words | `"payment to zomato"` | `"zomato"` |
| Remove short words (<3 chars) | `"to"`, `"by"` | removed |

**Bank keyword normalization:**
```
NEFT  → transfer
IMPS  → transfer
RTGS  → transfer
UPI   → upi
ATM   → atm
POS   → pos
EMI   → emi
```

---

### Step 6 — ML Classification

**File:** `app/services/classifier.py`

Each transaction description goes through a **two-stage hybrid classifier**:

#### Stage 1: Rule-Based Classification (Priority Order)

Rules are checked first because they are faster and more reliable for well-known merchants/keywords. Rules run in strict priority order to avoid conflicts:

| Priority | Category | Example Keywords |
|---|---|---|
| 1 | Income | salary, credited, income, bonus, refund |
| 2 | Cashback | cashback, reward, points |
| 3 | Medical | hospital, pharmacy, apollo, 1mg, doctor |
| 4 | Bills | electricity bill, airtel, jio, rent payment |
| 5 | Investment | mutual fund, sip, zerodha, groww, ppf |
| 6 | Food | zomato, swiggy, restaurant, bigbasket |
| 6 | Transport | uber, ola, petrol, fastag |
| 6 | Shopping | amazon, flipkart, myntra |
| 6 | Entertainment | netflix, spotify, hotstar |
| 6 | Education | university, fees, tuition |
| 6 | ATM | atm, cash withdrawal |
| 6 | Transfer | neft, imps, rtgs, sent to |

If a rule matches → category assigned with **95% confidence**, skip Stage 2.

**Important:** If `transaction_type = 'debit'` is known, Income and Cashback rules are skipped — a debit transaction cannot be income.

#### Stage 2: ML Classification (TF-IDF + LinearSVC)

If no rule matches:
1. The cleaned text is transformed using the **fitted TF-IDF vectorizer** (150 features, 1–3 grams)
2. The **LinearSVC model** predicts the category
3. The **decision function** score is converted to a confidence value using sigmoid: `confidence = 1 / (1 + e^(-score))`
4. Confidence is clamped between 0.50 and 0.95

All transactions are classified in **batch mode** for efficiency — the entire DataFrame is vectorized and predicted in one operation.

After classification, the database is updated with the category and confidence for each transaction.

---

### Step 7 — Financial Summary Calculation

**File:** `app/services/summary.py`

1. Transactions are split by `transaction_type`:
   - All `credit` transactions → summed into **Total Income**
   - All `debit` transactions → summed into **Total Expense**

2. Debit transactions are grouped by `category` to build the **category breakdown** (used for pie chart):
   ```
   Food:        ₹3,200
   Transport:   ₹1,800
   Bills:       ₹4,500
   Shopping:    ₹2,100
   ...
   ```

3. **Income and Cashback categories are excluded from the category breakdown** — they only contribute to Total Income, never appear as expense categories.

4. **Net Balance** = Total Income − Total Expense (can be negative if expenses exceed income)

5. Summary is stored in the `financial_summaries` and `category_breakdowns` database tables.

---

### Step 8 — Online Learning

**File:** `ml-service/online_learning.py`

After every upload, all classified transactions are saved to `new_transactions.csv` for future model retraining:
- Saves: description, category, amount, timestamp
- Works on a copy of the DataFrame (does not mutate the original)
- When 50+ new samples are collected, the system marks itself as **ready for retraining**

**Manual Retraining (triggered by user clicking "Retrain Model" button):**
1. Loads existing `training/dataset.csv`
2. Loads `new_transactions.csv`
3. Merges both datasets and removes duplicates
4. Re-runs the full training pipeline (TF-IDF + LinearSVC)
5. Saves new `svm_model.pkl` and `vectorizer.pkl`
6. Archives the new data to a timestamped history CSV
7. Clears `new_transactions.csv`
8. Reloads the classifier in memory with the new model

---

### Step 9 — Response Sent to Frontend

The ML service returns a JSON response containing:

```json
{
  "income": 66000.00,
  "expense": 29875.00,
  "remaining_balance": 36125.00,
  "categories": {
    "Food": 3200.00,
    "Transport": 1800.00,
    "Bills": 4500.00,
    "Shopping": 2100.00
  },
  "fileId": "uuid-string",
  "fileName": "statement.csv",
  "fileSize": 24576,
  "transactionCount": 120,
  "processedAt": "2026-05-22T10:30:00",
  "cleaningStats": {
    "originalRows": 125,
    "cleanedRows": 120,
    "removedRows": 5,
    "retentionRate": 96.0,
    "qualityScore": 92.5,
    "processingTime": 0.84
  },
  "databaseStored": true
}
```

This response travels: ML Service → Node.js Backend → React Frontend.

---

### Step 10 — Dashboard Rendered

**File:** `frontend/src/components/Dashboard.js`

The frontend renders the analysis results:

1. **KPI Cards** — Total Income, Total Expense, Net Balance (green if positive, red if negative)
2. **Bar Chart** — Income vs Expense side-by-side comparison
3. **Pie Chart** — Expense breakdown by category (Income/Cashback excluded)
4. **Category Table** — Sorted by amount, shows each category's share as a progress bar
5. **AI Learning Progress** — Shows how many new samples have been collected toward the next retraining threshold (50 samples)
6. **Invest Advice Button** — Navigates to the Investment Advice page

---

## 6. Transaction Classification System

### Classification Decision Flow

```
Raw Description
      │
      ▼
NLP Text Cleaning
      │
      ▼
Rule-Based Check (Priority 1–6)
      │
      ├── Match Found? ──► Assign Category (95% confidence)
      │
      └── No Match
            │
            ▼
      TF-IDF Vectorization
            │
            ▼
      LinearSVC Prediction
            │
            ▼
      Confidence Score (sigmoid of decision function)
            │
            ▼
      Assign Category (50–95% confidence)
```

### Confidence Scoring

| Source | Confidence Range | Meaning |
|---|---|---|
| Rule-based match | 95% | High certainty keyword match |
| ML — strong prediction | 80–95% | Model is very confident |
| ML — moderate prediction | 65–80% | Model is reasonably confident |
| ML — weak prediction | 50–65% | Model is uncertain |
| Empty/unreadable text | 50% | Fallback to "Others" |

---

## 7. Investment Advice Engine

**File:** `ml-service/investment_advisor.py`

When the user clicks "Invest Advice", the system:

1. **Determines Risk Profile** based on remaining balance:
   - Balance < ₹10,000 → Low Risk
   - Balance ₹10,000–₹50,000 → Medium Risk
   - Balance > ₹50,000 + savings rate > 30% → High Risk
   - Balance > ₹50,000 + savings rate ≤ 30% → Medium Risk

2. **Fetches Market Data** (with 5-minute cache):
   - Bitcoin price from CoinGecko API (live)
   - NIFTY 50 from Yahoo Finance API (live)
   - Gold/Silver from market estimates
   - Falls back to simulated data if APIs are unavailable

3. **Analyzes Market Trends** — generates Buy/Sell/Hold signals based on 24h price change:
   - Change > +2% and trending up → Strong Buy
   - Change > +0.5% and trending up → Buy
   - Change < -2% and trending down → Sell
   - Change < -0.5% and trending down → Caution
   - Otherwise → Hold

4. **Generates 3 Recommendations** — top 3 assets from the user's risk profile, sorted by market performance, with 40%/30%/30% allocation split

5. **Calculates Return Projections** for 1 year, 3 years, 5 years across 3 scenarios:
   - Conservative: 8% annual return
   - Moderate: 12% annual return
   - Aggressive: 18% annual return

**Investment options by risk profile:**
| Risk | Options |
|---|---|
| Low | Gold, Silver, Mutual Funds |
| Medium | Real Estate, Stocks, Mutual Funds |
| High | Bitcoin, Stocks, Diamond |

---

## 8. Online Learning System

**File:** `ml-service/online_learning.py`

The system continuously improves by learning from real uploaded data.

```
Every Upload
     │
     ▼
Save transactions to new_transactions.csv
     │
     ▼
Count reaches 50+?
     │
     ├── No  → Show progress bar on dashboard
     │
     └── Yes → Mark "Ready for Retraining"
                    │
                    ▼
              User clicks "Retrain Model"
                    │
                    ▼
              Merge new + existing training data
                    │
                    ▼
              Remove duplicates
                    │
                    ▼
              Re-train TF-IDF + LinearSVC
                    │
                    ▼
              Save new model files
                    │
                    ▼
              Archive new data to history CSV
                    │
                    ▼
              Reload classifier in memory
```

---

## 9. Database Schema

**Default:** SQLite (`finance_tracker.db`)
**Production:** PostgreSQL (via `DATABASE_URL` environment variable)

### Table: `transactions`
| Column | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment |
| file_id | String | Links to uploaded_files |
| description | Text | Transaction description |
| amount | Float | Transaction amount in ₹ |
| transaction_type | String | 'credit' or 'debit' |
| category | String | ML-assigned category |
| confidence | Float | Classification confidence (0–1) |
| created_at | DateTime | Record creation time |

### Table: `uploaded_files`
| Column | Type | Description |
|---|---|---|
| id | String (PK) | UUID |
| filename | String | Original filename |
| file_format | String | CSV / XLSX / PDF |
| file_size | Integer | Size in bytes |
| original_rows | Integer | Rows before cleaning |
| cleaned_rows | Integer | Rows after cleaning |
| removed_rows | Integer | Rows removed |
| retention_rate | Float | % of rows kept |
| quality_score | Float | Data quality score (0–100) |
| processing_time | Float | Seconds to process |
| uploaded_at | DateTime | Upload timestamp |
| processed | Boolean | Whether ML classification is done |

### Table: `financial_summaries`
| Column | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment |
| file_id | String | Links to uploaded_files |
| income | Float | Total credit amount |
| expense | Float | Total debit amount |
| remaining_balance | Float | Income minus expense |
| transaction_count | Integer | Total transactions |
| created_at | DateTime | Record creation time |

### Table: `category_breakdowns`
| Column | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment |
| file_id | String | Links to uploaded_files |
| category | String | Category name |
| amount | Float | Total amount for category |
| transaction_count | Integer | Number of transactions |
| created_at | DateTime | Record creation time |

---

## 10. API Endpoints Reference

### Backend (Node.js — Port 5000)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyze` | Upload and analyze bank statement |
| GET | `/api/categories` | Get list of all categories |
| GET | `/api/health` | Health check for both services |
| GET | `/api/learning/stats` | Get online learning progress |
| POST | `/api/learning/retrain` | Trigger model retraining |
| POST | `/api/investment/advice` | Get investment recommendations |

### ML Service (FastAPI — Port 8000)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze` | Core analysis pipeline |
| POST | `/classify` | Classify a single description |
| GET | `/categories` | List all categories |
| GET | `/health` | Service health check |
| GET | `/learning/stats` | Learning progress stats |
| POST | `/learning/retrain` | Trigger retraining |
| POST | `/investment/advice` | Investment advice |
| GET | `/cleaning/patterns` | Adaptive cleaner statistics |
| GET | `/cleaning/formats` | Known bank statement formats |
| GET | `/history` | Recent upload history |
| GET | `/summary/{file_id}` | Get stored summary by ID |

---

## 11. Supported File Formats

| Format | Extension | How It's Parsed |
|---|---|---|
| CSV | `.csv` | `pandas.read_csv()` |
| Excel | `.xlsx` | `pandas.read_excel()` |
| Excel (legacy) | `.xls` | `pandas.read_excel()` |
| PDF | `.pdf` | `pdfplumber` — table extraction first, text fallback |

**Required columns (any of these naming variations are auto-detected):**

| Standard Name | Accepted Variations |
|---|---|
| description | description, narration, transaction details, particulars, details, remarks, transaction, desc |
| amount | amount, value, transaction amount |
| debit | debit, withdrawal, dr, paid, withdraw, debit amount |
| credit | credit, deposit, cr, received, deposited, credit amount |

---

## 12. Categories Reference

### Income Categories (go to Total Income only, never shown in expense breakdown)
| Category | Keywords |
|---|---|
| Income | salary, credited, income, bonus, refund |
| Cashback | cashback, reward, points |

### Expense Categories (shown in pie chart and category table)
| Category | Example Transactions |
|---|---|
| Food | Zomato, Swiggy, restaurant, BigBasket, grocery |
| Transport | Uber, Ola, petrol, FASTag, metro |
| Shopping | Amazon, Flipkart, Myntra, Ajio |
| Bills | Electricity bill, Airtel, Jio, rent payment |
| Investment | Mutual fund SIP, Zerodha, Groww, PPF |
| Utilities | Electricity, water, gas, internet, mobile recharge |
| Entertainment | Netflix, Spotify, Hotstar, movie tickets |
| Education | University fees, tuition, Udemy, Coursera |
| Medical | Hospital, pharmacy, Apollo, 1mg, doctor |
| ATM | ATM cash withdrawal |
| Transfer | NEFT, IMPS, RTGS, sent to, paid to |
| Others | Anything not matching above rules or ML model |

---

*Documentation generated for Finance Tracker v1.0.0 — May 2026*
