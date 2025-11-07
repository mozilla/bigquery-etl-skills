# Existing Bigeye Collections

This file is auto-generated from existing bigconfig.yml files.
Use this to guide users toward consistent collection naming and notification channels.

**Last updated:** Run `./scripts/extract_collections.py` to refresh

---

## Most Common Collections

### Subscription Platform

- **Usage:** 16 tables
- **Datasets:** subscription_platform_derived
- **Notification Channels:**
  - `email:phlee@mozilla.com, srose@mozilla.com`
  - `slack:#de-bigeye-triage`

### Operational Checks

- **Usage:** 9 tables
- **Datasets:** firefox_ios_derived, firefoxdotcom_derived, google_ads_derived, microsoft_derived
- **Notification Channels:**
  - `slack:#de-bigeye-triage`

### Test

- **Usage:** 1 tables
- **Datasets:** org_mozilla_fenix_derived
- **Notification Channels:**
  - `slack:#ds-bigeye-triage`

---

## All Collections

| Collection Name | Usage Count | Datasets | Channels |
|----------------|-------------|----------|----------|
| Subscription Platform | 16 | subscription_platform_derived | 2 configured |
| Operational Checks | 9 | firefox_ios_derived, firefoxdotcom_derived, google_ads_derived (+1 more) | 1 configured |
| Test | 1 | org_mozilla_fenix_derived | 1 configured |

---

## Guidance for New Monitoring

**When adding monitoring to a new table:**

1. **Check the dataset** - If your dataset appears above, use the existing collection
2. **Check the team** - Look for collections related to your team/product
3. **Match notification channels** - Use the same channels as similar tables
4. **Create new collection** - Only if none of the above apply

### Collections by Dataset

- **firefox_ios_derived:** Operational Checks
- **firefoxdotcom_derived:** Operational Checks
- **google_ads_derived:** Operational Checks
- **microsoft_derived:** Operational Checks
- **org_mozilla_fenix_derived:** Test
- **subscription_platform_derived:** Subscription Platform
