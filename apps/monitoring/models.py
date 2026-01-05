"""
Monitoring models.

Placeholder for future monitoring models (alerts, SLOs, etc.).
Currently not needed; metrics and logs are external (Prometheus, ELK).
"""

from django.db import models


class MonitoringConfig(models.Model):
    """
    Configuration for monitoring and alerting.
    
    TODO: Implement alert rules, notification channels, SLO tracking.
    """

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Monitoring Config'
        verbose_name_plural = 'Monitoring Configs'

    def __str__(self):
        return self.name
