"""HistorianBridge — vendor-agnostic gateway in front of historian backends."""
from .config import GatewayConfig, load_from_env
from .factory import build_client
from .gateway import build_app

__all__ = ["GatewayConfig", "build_app", "build_client", "load_from_env", "__version__"]
__version__ = "0.1.0"
