# Phase 1 Platform Functionality Audit

## Task 1: Airports Domain Repair
- **Root Cause**: The `/api/v1/airports` endpoint was failing due to missing data. The database was empty, meaning searches for airports (e.g. BLR, DEL) returned 404 errors or empty lists.
- **Fix**: Created `seed_airports.py` to insert Indian airports (BLR, DEL, BOM, etc.) directly into the `airports` table using `asyncpg` within the `airlynk-api` container. Verified live data via curl.

## Task 2: Customer Auth Repair
- **Root Cause**: The customer web frontend running on `http://localhost:4000` was not included in the CORS `ALLOWED_ORIGINS` on the backend, causing preflight requests to fail during login/auth endpoints.
- **Fix**: Added `http://localhost:4000` to `.env.development` `ALLOWED_ORIGINS` and restarted the `airlynk-api` container to reload configurations. Verified that `authStore.ts` and `api.ts` correctly manage JWT tokens.

## Task 3: Geo Domain Contract Fix
- **Root Cause**: A mismatch in geospatial coordinate naming between Swagger and the actual implementation/frontend. Swagger and some backend parts expected `pickup_lat/lon`, whereas the frontend sent `pickup_lat/lng`.
- **Fix**: Standardized `lon` to `lng` across the backend services (pricing schema, dispatch engine, matching logic) to match the frontend expectations (`pickup_lng` and `dropoff_lng`).

## Task 4: Pricing Engine Repair
- **Root Cause**: Python's `Decimal` type was being serialized inconsistently causing floating-point artifacts and excessively long precision decimals in JSON responses, leading to frontend display issues or parsing errors.
- **Fix**: Added `@field_validator` hooks with `mode='before'` in `PricingRuleResponse` and `FareEstimateResponse` schemas to explicitly round monetary fields (like `base_fare`, `per_km_rate`, `estimated_fare`) to 2 decimal places before Pydantic model validation.

## Task 7: Operator Dashboard Real Data Migration
- **Root Cause**: The operator dashboard widgets (`SurgeMonitor.tsx`, `page.tsx`, `dispatch/page.tsx`, `bookings/page.tsx`) were using mocked local state data with `setInterval` loops instead of consuming backend APIs.
- **Fix**: Rewired the operator dashboard React Query hooks:
  1. Connected Dashboard health status to `http://localhost:8000/health`.
  2. Connected Bookings metrics to `GET /api/v1/bookings` (Active bookings count & list).
  3. Replaced mock chart/dispatch drivers arrays with empty states when data is unavailable.
  4. Rewrote `SurgeMonitor.tsx` to fetch live rates from `GET /api/v1/pricing/rules`.

## Pending Tasks (Browser E2E Verification)
- Task 5: Customer Booking Flow
- Task 6: Tracking Validation
- Task 8: End-to-end Verification
These require browser testing to ensure the integrated fixes produce a fully functional flow.
