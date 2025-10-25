"""
Compatibility layer for privacy-preserving ML integration.

This module re-exports the simplified integration and provides symbols expected
by other parts of the codebase, avoiding circular imports.
"""
from __future__ import annotations

# Provide a NUMPY_AVAILABLE flag expected by other modules
try:
    import numpy as _np  # noqa: F401
    NUMPY_AVAILABLE = True
except Exception:  # ImportError and others
    NUMPY_AVAILABLE = False

# Re-export the main integration service from the simplified implementation
from .privacy_ml_integration_simplified import PrivacyPreservingMLIntegration  # noqa: E402,F401


class TimeSeriesForecastingService:
    """Lightweight placeholder to satisfy imports.

    The actual Time Series functionality lives in
    `services.time_series_forecasting.TimeSeriesForecasting`.
    This placeholder avoids circular imports at module import time.
    """

    def __init__(self, *args, **kwargs) -> None:
        # Lazy import to avoid circular dependency at import time
        try:
            from .time_series_forecasting import TimeSeriesForecasting  # noqa: F401
        except Exception:
            # If import fails (e.g., during partial environment), keep placeholder minimal
            pass


class RiskStratificationService:
    """Lightweight placeholder to satisfy imports.

    The actual Risk Stratification service lives in
    `services.risk_stratification.RiskStratificationService` and is imported
    directly by the router as `RiskService`.
    """

    def __init__(self, *args, **kwargs) -> None:
        # Lazy import to avoid circular dependency at import time
        try:
            from .risk_stratification import RiskStratificationService as _RS  # noqa: F401
        except Exception:
            # Keep placeholder available even if optional deps are missing
            pass
