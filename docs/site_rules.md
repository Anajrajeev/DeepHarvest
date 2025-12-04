# Site-Specific Rules

DeepHarvest supports pattern-based site-specific rules without hardcoding domain names.

## Overview

Instead of hardcoding site-specific logic, you can define rules using regex patterns in your configuration. This makes the system flexible and maintainable.

## Configuration

Add `site_rules` to your `config.yaml`:

```yaml
site_rules:
  # Rules are matched in order by priority (higher first)
  - pattern: ".*twitter\\.com|.*x\\.com"
    use_browser_directly: true
    priority: 10
    reason: "Large headers require browser rendering"
  
  - pattern: ".*wikipedia\\.org"
    require_js: true
    custom_user_agent: "DeepHarvest/1.0 (Wikipedia-compatible)"
    priority: 10
    reason: "Wikipedia requires proper user agent"
  
  - pattern: ".*"
    priority: 0
    reason: "Default rule"
```

## Rule Properties

- **pattern**: Regex pattern to match URLs (required)
- **use_browser_directly**: Use browser scraper directly (bypass HTTP fetch)
- **require_js**: Require JavaScript rendering
- **custom_user_agent**: Custom User-Agent header for this site
- **custom_headers**: Custom HTTP headers dict
- **link_extraction_strategy**: Link extraction strategy (future use)
- **priority**: Rule priority (higher = checked first, default: 0)
- **reason**: Human-readable reason for the rule

## Automatic Detection

DeepHarvest also uses heuristics to automatically detect sites needing special handling:

- Very short HTML (< 500 chars) → likely needs JS
- React/Angular indicators → requires JS
- SPA patterns (many divs, few links) → requires JS
- Link extraction issues → may need JS retry

## Examples

### Twitter/X Pattern

```yaml
- pattern: ".*twitter\\.com|.*x\\.com"
  use_browser_directly: true
  priority: 10
```

### Wikipedia Pattern

```yaml
- pattern: ".*wikipedia\\.org"
  require_js: true
  custom_user_agent: "DeepHarvest/1.0 (+https://github.com/deepharvest/deepharvest)"
  priority: 10
```

### SPA Detection

```yaml
- pattern: ".*\\.(spa|app)$|.*/spa/|.*/app/"
  require_js: true
  priority: 5
```

## Benefits

1. **No Hardcoding**: All rules are configurable
2. **Pattern-Based**: Use regex for flexible matching
3. **Priority System**: Control rule precedence
4. **Extensible**: Easy to add new rules
5. **Auto-Detection**: Heuristics catch unknown cases

