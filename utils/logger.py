import logging
import os
from datetime import datetime

def setup_logger():
    """配置系统日志"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    filename = datetime.now().strftime("%Y-%m-%d.log")
    log_path = os.path.join(log_dir, filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("HuiyanEngine")