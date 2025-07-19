"""
Centralized logging configuration for the blockchain network.
Provides both console and file logging with Rich formatting.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

# Install rich traceback handler for better error display
install(show_locals=True)

class NodeAddressFormatter(logging.Formatter):
    """Custom formatter that includes node address in log format."""
    
    def __init__(self, node_address: Optional[str] = None):
        super().__init__()
        self.node_address = node_address or "NO_NODE"
    
    def format(self, record):
        # Add node address to the record
        record.node_address = self.node_address[:8] if len(self.node_address) > 8 else self.node_address
        return super().format(record)

def setup_logging(
    node_address: Optional[str] = None,
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    console_log: bool = True,
    file_log: bool = True
) -> logging.Logger:
    """
    Set up centralized logging configuration.
    
    Args:
        node_address: Address of the node for identification in logs
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files (defaults to ./logs)
        console_log: Whether to enable console logging
        file_log: Whether to enable file logging
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("blockchain_network")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Create formatters
    console_formatter = NodeAddressFormatter(node_address)
    console_formatter._style = logging.PercentStyle(
        "[%(asctime)s] [%(levelname)s] [%(node_address)s] %(name)s: %(message)s"
    )
    
    file_formatter = NodeAddressFormatter(node_address)
    file_formatter._style = logging.PercentStyle(
        "%(asctime)s [%(levelname)s] [%(node_address)s] %(name)s: %(message)s"
    )
    
    # Console handler with Rich (no custom formatter)
    if console_log:
        console = Console()
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            log_time_format="[%X]"
        )
        logger.addHandler(rich_handler)
    
    # File handler
    if file_log:
        if log_dir is None:
            log_dir = "logs"
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create filename with node address and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if node_address:
            safe_address = "".join(c for c in node_address if c.isalnum() or c in "-_.").rstrip()
            log_filename = f"blockchain_{safe_address}_{timestamp}.log"
        else:
            log_filename = f"blockchain_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_path / log_filename)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name for the logger (usually __name__ of the module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"blockchain_network.{name}")

# Global logger instance for backward compatibility
logger = get_logger(__name__)