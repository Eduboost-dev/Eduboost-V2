from __future__ import annotations

from scripts.final_gate_classifier import FinalGateRefresh, build_refresh, write_refresh, BETA_CRITICAL_IDS

__all__ = ["FinalGateRefresh", "build_refresh", "write_refresh", "BETA_CRITICAL_IDS"]

if __name__ == "__main__":
    result = write_refresh()
    print(result.beta_decision)
