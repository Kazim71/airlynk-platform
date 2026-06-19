# AIRLYNK PHASE 2.5 STABILIZATION SPRINT

STOP BUILDING NEW DOMAINS.

STOP BUILDING NEW FRONTENDS.

STOP BUILDING NEW DASHBOARDS.

STOP GENERATING IMPLEMENTATION PLANS.

The recent audit identified that AirLynk is a strong architectural prototype but not yet an MVP.

Your mission is to convert the current prototype into a fully functioning system before any additional features are added.

---

# PRIMARY OBJECTIVE

Make the CURRENT platform work.

Do not add:

- Driver App
- Admin Portal
- Marketing Website
- Mobile App
- Loyalty Program
- Analytics Platform

Focus only on stabilization.

---

# TASK 1 - ENVIRONMENT STABILIZATION

Verify:

- Docker stack starts cleanly
- PostgreSQL connects successfully
- Redis connects successfully
- RabbitMQ connects successfully
- API boots successfully
- Celery boots successfully

Deliver:

runtime_status.md

Include:

- docker compose ps
- health endpoint results
- failing containers
- fixes applied

---

# TASK 2 - FLEET DOMAIN COMPLETION

Current audit finding:

Fleet models exist.

Fleet API does not exist.

Create:

/api/v1/fleet/drivers
/api/v1/fleet/vehicles

Implement:

- create driver
- update driver
- list drivers
- activate/deactivate driver

Implement:

- create vehicle
- update vehicle
- list vehicles

Follow existing architecture:

API → Service → Repository

Add:

- RBAC
- Tests
- OpenAPI docs

Deliver:

fleet_domain_walkthrough.md

---

# TASK 3 - BOOKING ↔ PRICING INTEGRATION

Audit found:

Booking service uses hardcoded pricing.

Current:

45 \* passenger_count

Remove this.

Booking creation must:

1. Call pricing service
2. Generate fare estimate
3. Store pricing breakdown
4. Persist actual calculated fare

Verify:

pricing estimate == booking price

Deliver:

pricing_integration_report.md

---

# TASK 4 - DISPATCH SECURITY

Audit found:

Dispatch endpoints have no authentication.

Apply:

JWT authentication

Apply:

Role protection

Allowed:

Operator
Platform Admin

Verify:

Unauthorized requests fail.

Deliver:

dispatch_security_report.md

---

# TASK 5 - REALISTIC SEED DATA

Generate:

20 Drivers

20 Vehicles

50 Bookings

10 Pricing Rules

10 Airports

Seed:

Delhi
Mumbai
Bangalore
Hyderabad
Chennai
Pune
Kolkata
Ahmedabad
Goa
Jaipur

No US cities.

No UK cities.

No New York.

No London.

No San Francisco.

Everything must use Indian airport transfer data.

Deliver:

seed_data_report.md

---

# TASK 6 - E2E BOOKING VERIFICATION

Create:

operator
customer
driver

Test flow:

1 Register customer

2 Login customer

3 Get airport list

4 Estimate fare

5 Create booking

6 Trigger dispatch

7 Assign driver

8 Start trip

9 Complete trip

Verify:

RabbitMQ events

Redis updates

Database records

WebSocket events

Deliver:

e2e_verification.md

---

# SUCCESS CRITERIA

Only declare success if:

- Docker healthy
- Fleet API exists
- Pricing integrated
- Dispatch secured
- Indian seed data loaded
- E2E booking flow passes

If any item fails:

STOP

Produce blocker report.

Do not continue building features.

Do not generate future plans.

Do not claim completion without runtime verification.