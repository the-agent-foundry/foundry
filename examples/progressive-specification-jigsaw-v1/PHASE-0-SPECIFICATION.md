# Workshop Booking Release Planner

## Problem and initiating frustration

A fictional community workshop currently coordinates room bookings through email and a shared spreadsheet. Staff repeatedly create overlapping reservations, cannot see who changed a booking, and spend time rebuilding the weekly schedule by hand.

## Proposed product and behavior

Build a small internal booking application that gives authorized staff one schedule, rejects overlapping reservations, records every accepted change, and exports the next seven days as a printable schedule. The first release uses manual staff entry; it does not accept public bookings.

## Success and acceptance criteria

- **REQ-001 - booking lifecycle:** authorized staff can create, update, and cancel a reservation with room, start time, end time, activity, and coordinator.
- **REQ-002 - collision safety:** the system rejects any active reservation whose room and time interval overlap an existing active reservation.
- **REQ-003 - auditability:** every accepted create, update, or cancellation records actor, action, timestamp, and before/after booking state.
- **REQ-004 - weekly output:** staff can generate a printable seven-day schedule from the current accepted booking state.
- **REQ-005 - recovery:** a failed write leaves the prior accepted state intact and reports a clear retryable error.

## Users and operating context

The users are a small group of authenticated workshop staff operating from modern desktop browsers. One staff role is sufficient for the first release. The application is an internal coordination tool, not a public marketplace or payment system.

## Controlling owner decisions and delegated freedom

The owner controls the user group, internal-only destination, required booking fields, collision rule, audit requirement, weekly output, non-goals, and launch decision. The orchestrator may choose ordinary implementation details, data structures, framework, and test tooling provided the blueprint preserves these decisions and remains portable.

## Non-goals and authority boundaries

The first release excludes public self-service booking, payments, customer accounts, automated email or text notifications, multi-site scheduling, analytics, and production deployment. Specification readiness grants no authority to implement, deploy, send messages, create accounts, purchase services, or change live systems.

## Unacceptable failures, risks, and unresolved assumptions

Unacceptable failures are silent double-booking, loss of accepted bookings, unaudited changes, or a schedule generated from stale state without warning. The main unresolved assumption is that one staff role and one time zone are sufficient. Concurrent writes and time-boundary behavior require explicit verification.

## Evidence that would change the destination

The destination should be reconsidered if staff need public booking, multiple permission levels, payment collection, recurring-series semantics, offline operation, multiple time zones, or integration with an existing authoritative calendar. Any of those changes requires a new owner-approved specification generation.

## Builder handoff shape

The final handoff must contain dependency-ordered build cells, requirement and decision traceability, interfaces, state owners, invariants, failure behavior, allowed and protected surfaces, verification, activation boundaries, rollback, and readback. It must end with `READY_FOR_BUILDER` and `BUILD_NOT_STARTED` and must not launch a builder.

## Recommendation and material alternatives

Recommend a single internal web application with one transactional booking store and a server-side collision check. A calendar SaaS integration could reduce custom work but would make audit and collision semantics depend on a third party. A spreadsheet macro is cheaper but does not reliably satisfy concurrent-write safety or auditability.
