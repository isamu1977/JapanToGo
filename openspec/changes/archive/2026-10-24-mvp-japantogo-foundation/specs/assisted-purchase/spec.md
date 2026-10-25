## ADDED Requirements

### Requirement: Assisted Purchase Pre-Order Submission
The system SHALL allow clients to create an Assisted Purchase pre-order containing one or more product items, specifying product URL, item name, quantity, unit price in JPY, and optional specifications (size, color, notes).

#### Scenario: Submitting a valid assisted purchase order
- **WHEN** a client submits a pre-order with type `assisted_purchase` and a list of items with valid URLs, names, quantities >= 1, and prices > 0 JPY
- **THEN** the system persists the pre-order with status `submitted`, associates each item, computes the service fee and total amount, and returns the created order summary

#### Scenario: Submitting without items
- **WHEN** a client attempts to submit an assisted purchase pre-order with an empty items array
- **THEN** the system rejects the submission with a 422 Unprocessable Entity error

### Requirement: Service Fee Calculation with Floor Rule
The system SHALL calculate a 20% service fee on the sum of all item prices, enforcing a minimum floor fee of ¥ 2.000 whenever the total items price is strictly below ¥ 10.000 JPY.

#### Scenario: Order total below 10,000 JPY
- **WHEN** an assisted purchase order has total item cost of ¥ 6.000 JPY
- **THEN** the system calculates the service fee as ¥ 2.000 JPY (floor applied) and total payable as ¥ 8.000 JPY

#### Scenario: Order total at or above 10,000 JPY
- **WHEN** an assisted purchase order has total item cost of ¥ 25.000 JPY
- **THEN** the system calculates the service fee as 20% (¥ 5.000 JPY) and total payable as ¥ 30.000 JPY

### Requirement: Admin Purchase Management and Domestic Tracking
The system SHALL provide an administrative endpoint to update the status of assisted purchase pre-orders to `purchased` and record the Japanese domestic tracking code.

#### Scenario: Admin marks order as purchased
- **WHEN** an administrator submits a domestic tracking code and updates status to `purchased` for a submitted order
- **THEN** the system updates the pre-order record, stores the tracking number, updates `updated_at`, and notifies the client of the purchase
