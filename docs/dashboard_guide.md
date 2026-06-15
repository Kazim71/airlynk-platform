# Dashboard Guide

AirLynk provides 8 default Grafana dashboards provisioned automatically upon startup.

## Dashboards

1. **API Overview (`api-overview.json`)**
   - Tracks total HTTP requests, 5xx error rates, active connections, and p95 latency.

2. **Booking Lifecycle (`booking-lifecycle.json`)**
   - Tracks bookings created and completed. Helps analyze conversion and drop-off.

3. **Dispatch Operations (`dispatch-operations.json`)**
   - Monitors the Matching and Assignment Engine. Includes attempts, retries, driver acceptances, and timeouts.

4. **WebSocket & Realtime (`websocket-realtime.json`)**
   - Monitors active socket connections and the broadcast message rate.

5. **Celery Workers (`celery-workers.json`)**
   - Visualizes Celery task duration percentiles.

6. **RabbitMQ Queues (`rabbitmq-queues.json`)**
   - Monitors message publish/consume rates and any publish failures.

7. **Redis Health (`redis-health.json`)**
   - Monitors Redis operation failure rates.

8. **Platform Health / System Overview**
   - General system overview combining high-level metrics.
