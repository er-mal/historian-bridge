"""axon_historian — abstract historian client.

Provides one Protocol (`HistorianClient`) that all backends implement. Apps
import the protocol; concrete drivers are loaded by entry-point or directly.

Backends shipped here:
  - InMemoryHistorian   (testing, fixtures)
  - InfluxHistorian     (InfluxDB 2.x, optional dep)
  - PiWebApiHistorian   (OSIsoft PI Web API, http only — no DCOM)
  - OpcUaHistorian      (asyncua, current values + history read, optional dep)

Apps should depend on axon_historian.HistorianClient and accept any
implementation, so `confidence in driver swap` becomes a config decision.
"""
from .base import HistorianClient, ConnectionInfo
from .memory import InMemoryHistorian

__all__ = ["HistorianClient", "ConnectionInfo", "InMemoryHistorian"]
__version__ = "0.1.0"
