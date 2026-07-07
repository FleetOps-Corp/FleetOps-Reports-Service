from functools import lru_cache

from fleetops_reports.config.settings import SecuritySettings


@lru_cache
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()
