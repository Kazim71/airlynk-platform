# ADR 006: Redis GEO for Location Tracking

## Status
Accepted

## Context
We need to track live driver locations and query nearby drivers efficiently for dispatching. Doing this in PostgreSQL with PostGIS for every heartbeat would overwhelm the primary database.

## Decision
We use Redis GEO commands (`GEOADD`, `GEORADIUS`/`GEOSEARCH`) to maintain the real-time spatial index of active drivers.

## Consequences
Pros: Sub-millisecond latency for spatial queries, offloads the primary DB.
Cons: Location data in Redis is ephemeral. Historical paths must be persisted separately if required for audit.
