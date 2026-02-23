"""
FastAPI ML Service for Finance Tracker
Handles file upload and ML classification with PostgreSQL storage
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import ML modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.classifier import TransactionClassifier
from app.services.summary import calculate_summary
from online_learning import learner
from data_cleaning_pipeline import DataCleaningPipeline
from investment_advisor import advisor

# Import database modules
from database import get_db, init_db
from db_manager import DatabaseManager

# Initialize FastAPI app
app = FastAPI(
    title="Finance Tracker ML API",
    description="Machine Learning service for transaction classification",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML classifier and cleaning pipeline (load once at startup)
classifier = None
cleaning_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Load ML model, initialize pipeline, and setup database on startup"""
    global classifier, cleaning_pipeline
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Load ML models
        classifier = TransactionClassifier()
        cleaning_pipeline = DataCleaningPipeline()
        print("✅ ML model loaded successfully")
        print("✅ Data cleaning pipeline initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Finance Tracker ML API",
        "version": "1.0.0",
        "model_loaded": classifier is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_status": "loaded" if classifier else "not loaded",
        "categories": 15
    }

@app.get("/categories")
async def get_categories():
    """Get list of available categories"""
    return {
        "income": ["Income", "Cashback"],
        "expense": [
            "Food",
            "Transport",
            "ATM",
            "Shopping",
            "Bills",
            "Investment",
            "Utilities",
            "Entertainment",
            "Transfer",
            "Education",
            "Medical",
            "Others"
        ]
    }

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Analyze bank statement file and return financial summary
    
    Enhanced Pipeline: Upload → Pandas Clean → PostgreSQL Store → Retrieve → NLP → ML → Summary
    
    Accepts: CSV, Excel (.xlsx, .xls), PDF
    Returns: JSON with income, expense, balance, categories, and cleaning stats
    """
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (10MB limit)
    file_size = 0
    temp_file = None
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            temp_file = temp.name
            
            # Read and save file
            content = await file.read()
            file_size = len(content)
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum size: 10MB"
                )
            
            temp.write(content)
        
        print(f"\n{'='*70}")
        print(f"📄 Processing: {file.filename} ({file_size} bytes)")
        print(f"{'='*70}")
        
        # PIPELINE STEP 1: Data Cleaning with Pandas
        print("\n🔹 STEP 1: DATA CLEANING (PANDAS)")
        try:
            df, cleaning_stats = cleaning_pipeline.clean_file(temp_file)
            print(f"✅ Pandas cleaning complete: {len(df)} clean transactions")
        except ValueError as e:
            print(f"❌ Data cleaning error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Data cleaning failed: {str(e)}. Please check your file format and column names."
            )
        except Exception as e:
            print(f"❌ Unexpected cleaning error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clean data: {str(e)}"
            )
        
        # Check if we have data after cleaning
        if len(df) == 0:
            raise HTTPException(
                status_code=400,
                detail="No valid transactions found after cleaning. Please check your file."
            )
        
        # PIPELINE STEP 2: Store in PostgreSQL using SQLAlchemy ORM
        print("\n🔹 STEP 2: STORE IN POSTGRESQL (SQLALCHEMY ORM)")
        try:
            db_manager = DatabaseManager(db)
            file_info = {
                'filename': file.filename,
                'format': file_ext[1:].upper(),
                'size': file_size
            }
            file_id = db_manager.store_cleaned_data(df, file_info, cleaning_stats)
            print(f"✅ Data stored in PostgreSQL with file_id: {file_id}")
        except Exception as e:
            print(f"❌ Database storage error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store data in database: {str(e)}"
            )
        
        # PIPELINE STEP 3: Retrieve from PostgreSQL
        print("\n🔹 STEP 3: RETRIEVE FROM POSTGRESQL")
        try:
            df = db_manager.retrieve_cleaned_data(file_id)
            print(f"✅ Retrieved {len(df)} transactions from database")
        except Exception as e:
            print(f"❌ Database retrieval error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve data from database: {str(e)}"
            )
        
        # PIPELINE STEP 4: NLP Processing (part of classification)
        print("\n🔹 STEP 4: NLP PROCESSING")
        print(f"✅ NLP text cleaning applied")
        
        # PIPELINE STEP 5: ML Classification
        print("\n🔹 STEP 5: ML CLASSIFICATION")
        df['category'] = classifier.classify_batch(df['description'].tolist())
        print(f"✅ Classification complete")
        
        # Update classifications in database
        db_manager.update_classifications(file_id, df)
        
        # PIPELINE STEP 6: Financial Summary
        print("\n🔹 STEP 6: FINANCIAL SUMMARY")
        summary = calculate_summary(df)
        print(f"✅ Summary calculated")
        
        # Store summary in database
        summary_with_count = {**summary, 'transactionCount': len(df)}
        db_manager.store_summary(file_id, summary_with_count)
        
        # PIPELINE STEP 7: Online Learning
        print("\n🔹 STEP 7: ONLINE LEARNING")
        try:
            learner.save_batch_transactions(df[['description', 'category', 'amount']].copy())
            print(f"✅ Transactions saved for learning")
        except Exception as e:
            print(f"⚠️  Failed to save for learning: {e}")
        
        # Build response with enhanced cleaning stats
        result = {
            **summary,
            "fileId": file_id,
            "fileName": file.filename,
            "fileSize": file_size,
            "transactionCount": len(df),
            "processedAt": datetime.now().isoformat(),
            "cleaningStats": {
                "originalRows": cleaning_stats['original_rows'],
                "cleanedRows": cleaning_stats['cleaned_rows'],
                "removedRows": cleaning_stats['removed_rows'],
                "retentionRate": round(
                    (cleaning_stats['cleaned_rows'] / cleaning_stats['original_rows'] * 100), 1
                ) if cleaning_stats['original_rows'] > 0 else 0,
                "format": cleaning_stats['format'],
                "cleaningSteps": cleaning_stats['cleaning_steps'],
                "qualityScore": round(cleaning_stats.get('quality_score', 0), 1),
                "processingTime": round(cleaning_stats.get('processing_time', 0), 2),
                "patternsFound": cleaning_stats.get('patterns_found', {}),
                "amountStats": cleaning_stats.get('amount_stats', {}),
                "anomaliesDetected": cleaning_stats.get('anomalies_detected', []),
                "warnings": cleaning_stats.get('warnings', [])
            },
            "databaseStored": True
        }
        
        print(f"\n{'='*70}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"{'='*70}\n")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except KeyError as e:
        print(f"❌ Column error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Missing required column: {str(e)}. Please ensure your file has 'description' and 'amount' columns (or debit/credit columns)."
        )
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        
        # Provide user-friendly error message
        error_msg = str(e)
        if "description" in error_msg.lower() or "amount" in error_msg.lower():
            detail = "File format error: Could not find required columns. Please ensure your file has a description column and an amount column (or debit/credit columns). See FILE_FORMAT_GUIDE.md for supported formats."
        else:
            detail = f"Failed to process file: {error_msg}"
        
        raise HTTPException(
            status_code=500,
            detail=detail
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass

@app.post("/classify")
async def classify_text(data: dict):
    """
    Classify a single transaction description
    
    Request body: {"description": "ZOMATO ORDER"}
    Returns: {"category": "Food"}
    """
    
    if "description" not in data:
        raise HTTPException(
            status_code=400,
            detail="Missing 'description' field"
        )
    
    description = data["description"]
    
    if not description or not description.strip():
        raise HTTPException(
            status_code=400,
            detail="Description cannot be empty"
        )
    
    try:
        category = classifier.classify(description)
        return {
            "description": description,
            "category": category
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )

@app.get("/learning/stats")
async def get_learning_stats():
    """
    Get statistics about online learning
    """
    new_samples = learner.get_new_samples_count()
    min_samples = learner.min_samples_for_retrain
    
    return {
        "new_samples_collected": new_samples,
        "min_samples_for_retrain": min_samples,
        "ready_for_retrain": new_samples >= min_samples,
        "progress_percentage": min(100, (new_samples / min_samples) * 100)
    }

@app.post("/learning/retrain")
async def trigger_retrain():
    """
    Manually trigger model retraining
    """
    try:
        success = learner.merge_and_retrain()
        
        if success:
            # Reload the classifier with new model
            global classifier
            classifier = TransactionClassifier()
            
            return {
                "status": "success",
                "message": "Model retrained successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "skipped",
                "message": "No new data to train on",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retraining failed: {str(e)}"
        )

@app.post("/investment/advice")
async def get_investment_advice(data: dict):
    """
    Get personalized investment advice based on financial data
    
    Request body: {
        "balance": 36125,
        "income": 66000,
        "expense": 29875
    }
    """
    
    if "balance" not in data or "income" not in data or "expense" not in data:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: balance, income, expense"
        )
    
    try:
        balance = float(data["balance"])
        income = float(data["income"])
        expense = float(data["expense"])
        
        # Generate investment advice
        advice = advisor.get_investment_advice(balance, income, expense)
        
        return advice
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid numeric values for balance, income, or expense"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate advice: {str(e)}"
        )

@app.get("/cleaning/patterns")
async def get_cleaning_patterns():
    """
    Get learned data cleaning patterns and statistics
    """
    try:
        from data_cleaning_pipeline import DataCleaningPipeline
        pipeline = DataCleaningPipeline()
        stats = pipeline.adaptive_cleaner.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "message": "Adaptive learning statistics"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patterns: {str(e)}"
        )

@app.get("/cleaning/formats")
async def get_known_formats():
    """
    Get list of known bank statement formats
    """
    try:
        from data_cleaning_pipeline import DataCleaningPipeline
        pipeline = DataCleaningPipeline()
        
        formats = {}
        for bank_name in pipeline.adaptive_cleaner.patterns['bank_formats'].keys():
            format_info = pipeline.adaptive_cleaner.get_format_info(bank_name)
            formats[bank_name] = {
                'columns': format_info.get('columns', []),
                'times_seen': format_info.get('times_seen', 0),
                'first_seen': format_info.get('first_seen', 'Unknown')
            }
        
        return {
            "status": "success",
            "formats": formats,
            "total_formats": len(formats)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get formats: {str(e)}"
        )

@app.get("/history")
async def get_upload_history(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get recent file upload history from database
    
    Args:
        limit: Number of recent files to retrieve (default: 10)
    """
    try:
        db_manager = DatabaseManager(db)
        history = db_manager.get_file_history(limit=limit)
        
        return {
            "status": "success",
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get history: {str(e)}"
        )

@app.get("/summary/{file_id}")
async def get_summary_by_id(file_id: str, db: Session = Depends(get_db)):
    """
    Retrieve stored summary by file_id from database
    
    Args:
        file_id: Unique file identifier
    """
    try:
        db_manager = DatabaseManager(db)
        summary = db_manager.get_summary_by_file_id(file_id)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary not found for file_id: {file_id}"
            )
        
        return {
            "status": "success",
            "file_id": file_id,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
