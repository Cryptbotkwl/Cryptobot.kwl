# Updated logger to ensure robust CSV logging, archiving, and include market trend data
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pandas as pd

# Set up logs directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure log formatter
log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Set up file handler with rotation
log_file = os.path.join(LOG_DIR, "bot.log")
file_handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure logger
logger = logging.getLogger("crypto-signal-bot")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False

def log_signal_to_csv(signal):
    # Log signal data to CSV with all required fields including market trend
    # Added btc_trend and ma200_status for better signal context
    try:
        csv_path = "logs/signals_log_new.csv"
        timestamp = signal.get("timestamp", pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')
        data = pd.DataFrame({
            "symbol": [signal.get("symbol", "")],
            "price": [signal.get("entry", "")],
            "direction": [signal.get("direction", "")],
            "tp1": [signal.get("tp1", "")],
            "tp2": [signal.get("tp2", "")],
            "tp3": [signal.get("tp3", "")],
            "sl": [signal.get("sl", "")],
            "confidence": [signal.get("confidence", 0)],
            "trade_type": [signal.get("trade_type", "")],
            "timestamp": [timestamp],
            "tp1_possibility": [signal.get("tp1_possibility", 0)],
            "tp2_possibility": [signal.get("tp2_possibility", 0)],
            "tp3_possibility": [signal.get("tp3_possibility", 0)],
            "conditions": [", ".join(signal.get("conditions", []))],
            "volume": [signal.get("volume", 0)],
            "quote_volume_24h": [signal.get("quote_volume_24h", 0)],
            "status": [signal.get("status", "pending")],
            "hit_timestamp": [signal.get("hit_timestamp", None)],
            "leverage": [signal.get("leverage", 10)],
            "btc_trend": [signal.get("btc_trend", 0)],  # Added BTC trend
            "ma200_status": [signal.get("ma200_status", "unknown")]  # Added MA200 status
        })

        if os.path.exists(csv_path):
            old_df = pd.read_csv(csv_path)
            if not data.empty:
                data = pd.concat([old_df, data], ignore_index=True)

        if not data.empty:
            data.to_csv(csv_path, index=False)
            logger.info(f"Signal logged to CSV for {signal.get('symbol', '')}")
        else:
            logger.error("No valid data to log to CSV")

        archive_old_logs(csv_path)

    except Exception as e:
        logger.error(f"Error logging signal to CSV: {e}")

def archive_old_logs(csv_path):
    # Archive old logs to prevent file size issues
    # Keep logs for last 7 days, archive older data
    try:
        if not os.path.exists(csv_path):
            return
        df = pd.read_csv(csv_path)
        if df.empty:
            return
        
        current_date = datetime.utcnow()
        week_ago = current_date - pd.Timedelta(days=7)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        old_data = df[df['timestamp'].dt.date < week_ago.date()]
        
        if not old_data.empty:
            archive_path = f"logs/archive/signals_log_{week_ago.strftime('%Y%m%d')}.csv"
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            old_data.to_csv(archive_path, index=False)
            new_data = df[df['timestamp'].dt.date >= week_ago.date()]
            new_data.to_csv(csv_path, index=False)
            logger.info(f"Archived {len(old_data)} old signals to {archive_path}")
    except Exception as e:
        logger.error(f"Error archiving logs: {e}")
