from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db
import logging
import time
from typing import Dict, Any

router = APIRouter(tags=["Health"])

def check_rabbitmq_connection(retries: int = 3) -> Dict[str, Any]:
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    for attempt in range(retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, 
                                       connection_attempts=3,
                                       retry_delay=2)
            )
            connection.close()
            return {"status": "healthy", "message": "RabbitMQ connection successful"}
        except Exception as e:
            if attempt == retries - 1:
                logging.error(f"RabbitMQ connection failed: {str(e)}")
                return {"status": "unhealthy", "message": str(e)}
            time.sleep(2)
            
def check_database_connection(db: Session, retries: int = 3) -> Dict[str, Any]:
    for attempt in range(retries):
        try:
            db.execute(text("SELECT 1"))
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            if attempt == retries - 1:
                logging.error(f"Database connection failed: {str(e)}")
                return {"status": "unhealthy", "message": str(e)}
            time.sleep(2)

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "api": {"status": "healthy"},
            "database": {"status": "unhealthy"},
            "payments": {"status": "unhealthy"},
            "rabbitmq": {"status": "unhealthy"}
        }
    }
    
    try:
        # Check database connection
        db_status = check_database_connection(db)
        health_status["components"]["database"] = db_status
        
        if db_status["status"] == "healthy":
            try:
                db.query(Payment).limit(1).all()
                health_status["components"]["payments"] = {
                    "status": "healthy",
                    "message": "Payment table accessible"
                }
            except Exception as e:
                health_status["components"]["payments"] = {
                    "status": "unhealthy",
                    "message": str(e)
                }
        
        # Check RabbitMQ connection
        rabbitmq_status = check_rabbitmq_connection()
        health_status["components"]["rabbitmq"] = rabbitmq_status
        
        if any(comp["status"] == "unhealthy" for comp in health_status["components"].values()):
            health_status["status"] = "unhealthy"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
            
        return health_status
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        logging.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )