# Test Plan Stub

1. **Schema Sanity**
   - Validate `artifacts/creatives.jsonl` with `creativespec`.
2. **Link Tracking**
   - Click through 3 generated URLs; confirm UTM params present.
3. **Lead ETL**
   - Run on 10 sample records; expect 10 valid `LeadRecord` items.
