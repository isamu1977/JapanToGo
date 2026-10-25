## MODIFIED Requirements

### Requirement: Warehouse Suite Address Display and One-Click Copy
The system SHALL provide clients with the official JapanToGo warehouse address in Japan, displaying it in Japanese kanji/kana and Romanized script, with the client's box identifier clearly labeled as "Código do seu Box: #JTG-XXXX" injected into the building complement line (`サンシャイン 4F #JTG-XXXX`), providing explicit instructions on attaching the Box code for sorting at the Osaka warehouse, offering one-click copy buttons with visual success feedback for each individual line as well as a quick action button to copy the complete formatted address, and representing the client's inventory in the navigation as "Meus Pacotes".

#### Scenario: Client views warehouse suite address
- **WHEN** a logged-in client views the address page in their dashboard
- **THEN** the system renders:
  - A prominent header card presenting "Código do seu Box: #JTG-XXXX" with one-click copy
  - Guidance explaining that the Box code is essential for package identification and check-in upon warehouse delivery
  - Japanese version with 氏名, 郵便番号, 都道府県, 市区町村, 丁目・番地・号, 建物名・部屋番号, and 電話番号
  - Romanized version with Name, Postal Code, Prefecture, City, Street / Number, Building / Unit, and Phone
  - Individual copy buttons with immediate visual feedback for each row
  - Quick action button to copy the full formatted address
