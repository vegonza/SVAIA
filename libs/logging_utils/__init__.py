from .logging_utils import SecureLogManager, FunctionMonitor
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

log_manager = SecureLogManager(log_file="logs/svaia.log")
function_monitor = FunctionMonitor(log_manager)

__all__ = ["log_manager", "function_monitor"]
