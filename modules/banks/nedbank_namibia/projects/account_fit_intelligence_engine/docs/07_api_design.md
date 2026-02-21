# API Design

## Purpose

This document outlines the future API design for the Account Fit Intelligence Engine, though v0.1 operates as a local Python module without an API layer.

## Scope

API design considerations for future versions when the engine may be deployed as a service.

## Observed

Standard API patterns in financial services:
- RESTful endpoints for resource access
- JSON request/response format
- Authentication and authorization
- Rate limiting and quotas

## Inferred

API requirements based on use cases:
- Customer account fit analysis endpoint
- Fee calculation endpoint
- Account comparison endpoint (v0.3+)
- Recommendation endpoint (v1.0+)

## Assumed

For API design:
- HTTP/REST is sufficient (no GraphQL needed initially)
- Synchronous processing adequate for v0.1 scale
- JSON is preferred format
- Authentication required for production

## Proposed

### v0.1: No API

v0.1 operates as a Python module with direct function calls. No API layer implemented.

**Usage Pattern:**
```python
from src.engine.account_fit import analyze_account_fit

result = analyze_account_fit(
    customer_id="CUST_001",
    account_type="silver_payu",
    config_path="configs/account_types/silver_payu.yaml"
)
```

### Future API Design (v0.3+)

**Base URL:** `https://api.banking-intelligence.example.com/v1`

#### Endpoint: Analyze Account Fit

**POST** `/accounts/analyze`

Calculate fees and fit score for a customer on a specific account type.

**Request:**
```json
{
  "customer_id": "CUST_001",
  "account_type_id": "silver_payu",
  "transaction_history_months": 6
}
```

**Response:**
```json
{
  "customer_id": "CUST_001",
  "account_type_id": "silver_payu",
  "analysis": {
    "monthly_fee_fixed": 30.00,
    "transaction_fee_estimate": 0.00,
    "total_monthly_estimate": 30.00,
    "behaviour_features": {
      "txn_count_monthly": 15.2,
      "transaction_diversity": 5
    },
    "notes": "Transaction fees unknown; estimates may vary"
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

#### Endpoint: Compare Accounts (v0.3+)

**POST** `/accounts/compare`

Compare multiple account types for a customer.

**Request:**
```json
{
  "customer_id": "CUST_001",
  "account_types": ["silver_payu", "savvy", "gold_payu"]
}
```

**Response:**
```json
{
  "customer_id": "CUST_001",
  "comparisons": [
    {
      "account_type_id": "silver_payu",
      "total_monthly_estimate": 30.00,
      "fit_score": 0.75
    },
    {
      "account_type_id": "savvy",
      "total_monthly_estimate": 25.00,
      "fit_score": 0.85
    }
  ],
  "recommendation": "savvy",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### API Design Principles

1. **RESTful:** Resource-oriented URLs
2. **Versioned:** /v1/ in URL for future compatibility
3. **JSON:** Standard request/response format
4. **Stateless:** No session state on server
5. **Secure:** HTTPS only, authentication required

### Authentication (Future)

**API Key Authentication:**
```
Authorization: Bearer <api_key>
```

**Rate Limiting:**
- 100 requests per minute per API key
- 429 Too Many Requests if exceeded

### Error Handling

**Standard Error Response:**
```json
{
  "error": {
    "code": "INVALID_CUSTOMER_ID",
    "message": "Customer ID not found",
    "details": "CUST_999 does not exist in database"
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

**HTTP Status Codes:**
- 200: Success
- 400: Bad Request (invalid input)
- 401: Unauthorized (missing/invalid auth)
- 404: Not Found (resource doesn't exist)
- 429: Too Many Requests (rate limit)
- 500: Internal Server Error

## Related Documentation

- See `04_system_architecture.md` for current architecture
- See `08_risk_and_compliance.md` for security considerations
