# PRD-00006: Complex ENV Value Parsing

## Problem

Env vars are strings. Lists and dicts can't be represented as plain strings.

## Solution

Pydantic auto-parses JSON for complex types. Use JSON syntax in env vars for lists/dicts.

## Syntax by Type

### Simple Scalars
```bash
BUVIS_DEBUG=true                    # bool
BUVIS_PAYROLL_BATCH_SIZE=500        # int
BUVIS_LOG_LEVEL=DEBUG               # str
```

### Lists
```bash
BUVIS_PAYROLL_PAYMENT_RULES='[{"rule_id":"overtime","enabled":true}]'
```

### Dicts
```bash
BUVIS_HCM_HEADERS='{"Authorization":"Bearer xxx","X-Api-Key":"yyy"}'
```

## Implementation

Pydantic handles JSON parsing automatically for typed fields:

```python
from pydantic import BaseModel

class PaymentRule(BaseModel):
    rule_id: str
    enabled: bool
    bonus_pct: float | None = None

class PayrollSettings(BaseSettings):
    payment_rules: list[PaymentRule] = []  # Accepts JSON array
    batch_size: int = 1000                  # Accepts plain int

    model_config = SettingsConfigDict(env_prefix="BUVIS_PAYROLL_")
```

## Shell Quoting

```bash
# Single quotes preserve JSON (recommended)
export BUVIS_RULES='[{"id":"a"},{"id":"b"}]'

# Double quotes require escaping
export BUVIS_RULES="[{\"id\":\"a\"}]"

# .env files - no outer quotes needed
BUVIS_RULES=[{"id":"a"},{"id":"b"}]
```

## Security Constraints

- **Validate structure**: JSON must match expected schema - reject extra fields
- **Size limits**: Reject unreasonably large JSON values (>64KB)
- **No code execution**: Pydantic validates, never evals
- **Sanitize before logging**: Don't log raw JSON (may contain secrets)

## Anti-patterns

- Don't use comma-separated values for lists (use JSON)
- Don't use custom delimiters (use JSON)
- Don't eval() or json.loads() manually - let Pydantic handle it

## Error Handling

| Error | Message |
|-------|---------|
| Invalid JSON | `Invalid JSON in BUVIS_RULES: Expecting ',' ...` |
| Wrong type | `BUVIS_RULES[0].enabled: Input should be a valid boolean` |
| Missing field | `BUVIS_RULES[0].rule_id: Field required` |

## Tests

1. `'[{"rule_id":"a","enabled":true}]'` -> `[PaymentRule(rule_id="a", enabled=True)]`
2. `'[]'` -> empty list
3. `'[{broken'` -> ValidationError with JSON parse error
4. `'[{"rule_id":123}]'` -> ValidationError (wrong type)
5. Plain scalar `500` still works for int fields
