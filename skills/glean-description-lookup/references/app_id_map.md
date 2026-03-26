# Glean App ID Map

Maps BigQuery dataset names to Glean Dictionary `app_id` values and known table names.

## Derivation Rule (General)

When the app_id is not listed below:

1. Take the BigQuery dataset name
2. Strip the `_live` or `_stable` suffix
3. The result is the Glean `app_id`

Examples:
- `firefox_desktop_live` → `firefox_desktop`
- `fenix_stable` → `fenix`
- `org_mozilla_firefox_live` → `org_mozilla_firefox`

For the table name:
- Take the BigQuery table name, strip the `_v<N>` suffix
- `newtab_v1` → `newtab`
- `events_v1` → `events`

URL pattern:
```
https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>
```

---

## Known App ID Mappings

| BigQuery Dataset | Glean app_id | Notes |
|---|---|---|
| `firefox_desktop_live` | `firefox_desktop` | Firefox desktop browser |
| `firefox_desktop_stable` | `firefox_desktop` | Firefox desktop browser |
| `fenix_live` | `fenix` | Firefox for Android (Fenix) |
| `fenix_stable` | `fenix` | Firefox for Android (Fenix) |
| `org_mozilla_fenix_live` | `org_mozilla_fenix` | Older Fenix package name |
| `org_mozilla_fenix_stable` | `org_mozilla_fenix` | Older Fenix package name |
| `org_mozilla_firefox_live` | `org_mozilla_firefox` | Firefox for Android (release) |
| `org_mozilla_firefox_stable` | `org_mozilla_firefox` | Firefox for Android (release) |
| `firefox_ios_live` | `firefox_ios` | Firefox for iOS |
| `firefox_ios_stable` | `firefox_ios` | Firefox for iOS |
| `focus_android_live` | `focus_android` | Focus for Android |
| `focus_android_stable` | `focus_android` | Focus for Android |
| `focus_ios_live` | `focus_ios` | Focus for iOS |
| `focus_ios_stable` | `focus_ios` | Focus for iOS |
| `klar_android_live` | `klar_android` | Klar for Android |
| `klar_ios_live` | `klar_ios` | Klar for iOS |
| `firefox_echo_show_live` | `firefox_echo_show` | Firefox for Echo Show |
| `firefox_fire_tv_live` | `firefox_fire_tv` | Firefox for Fire TV |
| `vrbrowser_live` | `vrbrowser` | Firefox Reality (VR) |
| `reference_browser_live` | `reference_browser` | Reference browser |
| `monitor_cirrus_live` | `monitor_cirrus` | Firefox Monitor |
| `rally_core_live` | `rally_core` | Firefox Rally core |

---

## Common Table Names by Ping Type

| BigQuery Table (strip `_v<N>`) | Glean ping | Typical fields |
|---|---|---|
| `events` | events ping | `events[]`, `client_info`, `metadata`, `metrics` |
| `metrics` | metrics ping | `metrics.*` (counter, string, boolean, etc.), `client_info` |
| `baseline` | baseline ping | `metrics.timespan.glean_baseline_duration`, `client_info`, `ping_info` |
| `newtab` | newtab ping | `metrics.*` (newtab-specific), `client_info`, `ping_info` |
| `first_session` | first session ping | `metrics.*`, `client_info` |
| `deletion_request` | deletion-request ping | `client_info.client_id`, `ping_info` |
| `crash` | crash ping | `metrics.*`, `client_info` |
| `spoc` | sponsored content ping | `metrics.*` (pocket/spoc metrics) |

---

## Token Risk by Table Type

| Table type | Typical field count | Strategy |
|---|---|---|
| `events` | 100–300+ | Targeted: request only fields from query.sql |
| `metrics` | 100–500+ | Targeted: request only fields from query.sql |
| `baseline` | 30–60 | Sectional: by category |
| `newtab` | 20–80 | Check count first |
| `first_session` | 10–30 | Usually safe to request full schema |
| `deletion_request` | < 10 | Safe to request full schema |
| `crash` | 30–100 | Check count first |

---

## Alternate app_id Variations

Some apps changed their package name over time. If a URL returns 404, try these alternates:

| Preferred app_id | Alternate |
|---|---|
| `fenix` | `org_mozilla_fenix`, `org_mozilla_firefox_beta`, `org_mozilla_fenix_nightly` |
| `org_mozilla_firefox` | `fenix`, `org_mozilla_fenix` |
| `firefox_ios` | `org_mozilla_ios_firefox` |

---

## Verification

If unsure whether an app_id is correct:
1. Visit https://dictionary.telemetry.mozilla.org/ and search for the app name
2. Browse to the app and find the table
3. Copy the URL — it contains the correct `app_id`
