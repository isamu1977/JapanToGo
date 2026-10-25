# shipping-and-consolidation Specification

## Purpose
Defines the consolidation of stored suite items into an international shipment (EMS or Small Packet) with a customs declaration and Brazilian recipient details, the administrative dispatch queue that records the international tracking code, and the export of shipment data in the Japan Post "International Mail My Page" format.
## Requirements
### Requirement: Suite Item Consolidation and Shipment Request
The system SHALL allow clients to select multiple available items from their suite (status `in_storage`), select an international shipping method (`ems` or `small_packet`), fill in customs declaration details (item descriptions, quantities, declared values in JPY), and provide the recipient's Brazilian CPF, telephone, and postal address.

#### Scenario: Client requests consolidation shipment
- **WHEN** a client selects 2 or more suite items with status `in_storage`, chooses `ems`, enters customs declaration with positive values and valid recipient CPF and address
- **THEN** the system creates a new `shipments` record with status `requested`, updates the selected suite items' status to `consolidation_requested`, and links them to the shipment

#### Scenario: Requesting shipment with missing customs declaration
- **WHEN** a client submits a shipment request with empty customs declaration or missing recipient CPF
- **THEN** the system rejects the submission with a 422 Unprocessable Entity error

### Requirement: Admin Dispatch Queue and International Tracking
The system SHALL provide administrators with a dispatch queue displaying pending shipments, allowing operators to enter final packed weight, shipping fee in JPY, and the official international tracking code (e.g. `EJ123456789JP`).

#### Scenario: Admin registers international dispatch
- **WHEN** an administrator inputs the final shipping fee and international tracking code for a packed shipment and confirms dispatch
- **THEN** the system transitions the shipment status to `dispatched`, sets `dispatched_at` timestamp, and transitions all associated suite items to `shipped`

### Requirement: Japan Post International Mail My Page Data Export
The system SHALL provide an export utility that formats shipment and recipient data into the standard schema used by the Japan Post "International Mail My Page" system for copy-paste or text export.

#### Scenario: Operator exports shipment for Japan Post
- **WHEN** an operator clicks "Exportar para Japan Post" on an approved shipment
- **THEN** the system outputs a formatted payload with Recipient Name, Country Code (BR), Postal Code, State/City, Address lines, Recipient Phone, Customs Item Names in English, Quantities, and Declared Values in JPY

