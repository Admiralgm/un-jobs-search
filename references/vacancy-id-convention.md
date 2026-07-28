# Vacancy ID Extraction Convention

To ensure deduplication and tracking accuracy, use these source-specific patterns to find the actual identifier for a job.

| Organization | ID Pattern | Location on Page / URL |
| :--- | :--- | :--- |
| **World Bank Group** | `req[0-9]{5}` (e.g., req36524) | Found under "Job #:" in the detail table or "reqXXXXX" in the URL. |
| **UNICEF** | Dual format: `JobSystemID/#RefNumber` (e.g., `593133/#00136822`) | **VACANCY ID** = PageUp Job System ID ("Job no:" field). **REF NUMBER** = `#XXXXXX` from job title. Log in tracker as `JobSystemID/#RefNumber`. |
| **ITU** | 10-digit numeric or VN | URL path (e.g., 1153253155) or "Requisition ID" in text. |
| **IOM** | 8-digit numeric or CFA/VN | Labeled as "Vacancy Notice Number" or in Detail URL. |
| **Impactpool** | 7-digit numeric | The unique ID in the URL structure (e.g., `/jobs/1212561`). |
| **ECB** | 121xxxx pattern | Numeric ID in the URL or "Reference number". |
| **UNOPS** | REQ-[0-9]* | Labeled "Vacancy code" or "Job ID". |

## Rule for Generation
If NO numeric or alphanumeric ID is found:
1. Concatenate `Title` + `Organization` + `Location`.
2. Generate a 6-digit hash using Python `hashlib.shake_256`.
3. Format as `[GEN-XXXXXX]`.
4. This ensures that the same job found in two different batches gets the same stable ID for deduplication.