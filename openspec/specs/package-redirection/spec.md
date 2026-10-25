# package-redirection Specification

## Purpose
Defines the pure redirection (forwarding) flow: registration of a package bought directly in a Japanese store with a mandatory purchase receipt, the warehouse check-in with rapid client search by suite code, weighing in grams, and the capture of up to five inspection photos per item.
## Requirements
### Requirement: Pure Redirection Pre-Order Registration
The system SHALL allow clients who buy directly from Japanese stores to submit a Redirection (`forwarding`) pre-order, providing expected incoming domestic tracking, store name, description, and an uploaded purchase receipt or invoice.

#### Scenario: Client submits redirection notice with receipt
- **WHEN** a client submits a pre-order with type `forwarding` including store name, description, domestic tracking code, and an uploaded valid receipt image/PDF
- **THEN** the system saves the receipt file, persists the pre-order with status `submitted`, and links it to the client's suite

#### Scenario: Client submits redirection notice without receipt
- **WHEN** a client attempts to submit a `forwarding` pre-order without providing a receipt attachment
- **THEN** the system rejects the request with a 422 Unprocessable Entity error stating that receipt upload is mandatory

### Requirement: Warehouse Check-in and Rapid Client Search
The system SHALL provide warehouse operators with a fast search interface to look up clients by `suite_code` (e.g., `JTG-1001`) or client name to register received packages.

#### Scenario: Operator finds client by suite code
- **WHEN** an operator inputs `JTG-1001` in the check-in search bar
- **THEN** the system returns matching user details and any pending pre-orders matching the domestic tracking or suite

#### Scenario: Operator checks in package
- **WHEN** an operator selects a client, enters the weighed package weight in grams (e.g. 1450g), description, and domestic tracking number
- **THEN** the system creates a new `suite_items` record with status `in_storage`, recorded weight, and sets `received_at` timestamp

### Requirement: Inspection Photos Capture and Storage
The system SHALL allow warehouse operators to upload or capture up to 5 inspection photos per received suite item, compressing and associating them with the item.

#### Scenario: Uploading 1 to 5 inspection photos
- **WHEN** an operator uploads between 1 and 5 photo files (JPEG/PNG/WebP) for a suite item
- **THEN** the system validates file types, processes images, stores them on the persistent storage volume, records `inspection_photos` records, and makes them visible in the client's suite gallery

#### Scenario: Uploading more than 5 photos
- **WHEN** an operator attempts to upload more than 5 inspection photos for a single item check-in
- **THEN** the system rejects the excess files with a validation error limiting inspection photos to a maximum of 5

