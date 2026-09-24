#!/usr/bin/env python3
"""Deprecated migration command.

CareerHub uses one unified software version from Motherpher/CareerHubZero.
Profile repositories do not receive propagated engine versions in the stable
architecture. They expose careerhub.yaml and execute the central body.
"""

raise SystemExit(
    "sync_stack_versions.py is deprecated: unified CareerHub profiles are not independently versioned."
)
