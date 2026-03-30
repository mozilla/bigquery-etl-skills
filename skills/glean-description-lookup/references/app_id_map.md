# Glean App ID Map

Maps BigQuery dataset names to Glean Dictionary `app_id` values and known table names.

> **Coverage note:** This map covers common apps. For the authoritative list of all Glean apps,
> fetch `https://probeinfo.telemetry.mozilla.org/glean/repositories`.
> For any app not listed here, the derivation rule below will produce the correct dictionary URL form.

## Derivation Rule (General)

When the app_id is not listed below:

1. Take the BigQuery dataset name
2. Strip the `_live` or `_stable` suffix
3. The result is the Glean Dictionary **URL form** of the app_id (uses underscores)

Examples:
- `firefox_desktop_live` → `firefox_desktop`
- `fenix_stable` → `fenix`
- `org_mozilla_firefox_live` → `org_mozilla_firefox`
- `net_thunderbird_android_stable` → `net_thunderbird_android`

For the table name:
- Take the BigQuery table name, strip the `_v<N>` suffix
- `newtab_v1` → `newtab`
- `events_v1` → `events`

URL pattern:
```
https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>
```

---

## ⚠️ Hyphen vs Underscore

| Context | Form | Example |
|---|---|---|
| Glean Dictionary URL (`dictionary.telemetry.mozilla.org`) | **underscores** | `firefox_desktop` |
| Probeinfo API (`probeinfo.telemetry.mozilla.org`) | **hyphens** | `firefox-desktop` |

The derivation rule (strip `_live`/`_stable`) gives the **underscore form** used in dictionary URLs.
When using the probeinfo API as a fallback, replace `_` with `-` in the app_id.

---

## Known App ID Mappings

| BigQuery Dataset | Glean app_id (URL form) | Notes |
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
| `org_mozilla_ios_firefox_live` | `org_mozilla_ios_firefox` | Firefox iOS (older package name) |
| `org_mozilla_ios_firefox_stable` | `org_mozilla_ios_firefox` | Firefox iOS (older package name) |
| `focus_android_live` | `focus_android` | Focus for Android |
| `focus_android_stable` | `focus_android` | Focus for Android |
| `org_mozilla_focus_live` | `org_mozilla_focus` | Focus for Android (package name) |
| `org_mozilla_focus_stable` | `org_mozilla_focus` | Focus for Android (package name) |
| `focus_ios_live` | `focus_ios` | Focus for iOS |
| `focus_ios_stable` | `focus_ios` | Focus for iOS |
| `org_mozilla_ios_focus_live` | `org_mozilla_ios_focus` | Focus for iOS (package name) |
| `klar_android_live` | `klar_android` | Klar for Android |
| `org_mozilla_klar_live` | `org_mozilla_klar` | Klar (package name) |
| `org_mozilla_ios_klar_live` | `org_mozilla_ios_klar` | Klar for iOS (package name) |
| `firefox_echo_show_live` | `firefox_echo_show` | Firefox for Echo Show |
| `firefox_fire_tv_live` | `firefox_fire_tv` | Firefox for Fire TV |
| `org_mozilla_tv_firefox_live` | `org_mozilla_tv_firefox` | Firefox for Fire TV (package name) |
| `vrbrowser_live` | `vrbrowser` | Firefox Reality (VR) |
| `org_mozilla_vrbrowser_live` | `org_mozilla_vrbrowser` | Firefox Reality (package name) |
| `reference_browser_live` | `reference_browser` | Reference browser |
| `org_mozilla_reference_browser_live` | `org_mozilla_reference_browser` | Reference browser (package name) |
| `monitor_cirrus_live` | `monitor_cirrus` | Firefox Monitor (Cirrus) |
| `monitor_backend_live` | `monitor_backend` | Firefox Monitor backend |
| `monitor_frontend_live` | `monitor_frontend` | Firefox Monitor frontend |
| `net_thunderbird_android_live` | `net_thunderbird_android` | Thunderbird for Android |
| `net_thunderbird_android_stable` | `net_thunderbird_android` | Thunderbird for Android |
| `thunderbird_desktop_live` | `thunderbird_desktop` | Thunderbird desktop |
| `thunderbird_desktop_stable` | `thunderbird_desktop` | Thunderbird desktop |
| `fxa_client_live` | `fxa_client` | Firefox Accounts client |
| `accounts_backend_live` | `accounts_backend` | Accounts backend |
| `accounts_frontend_live` | `accounts_frontend` | Accounts frontend |
| `accounts_cirrus_live` | `accounts_cirrus` | Accounts Cirrus |
| `relay_backend_live` | `relay_backend` | Firefox Relay backend |
| `nimbus_live` | `nimbus` | Nimbus experimentation |
| `nimbus_cirrus_live` | `nimbus_cirrus` | Nimbus Cirrus |
| `service_nimbus_live` | `service_nimbus` | Nimbus service |
| `mozillavpn_live` | `mozillavpn` | Mozilla VPN |
| `mozillavpn_stable` | `mozillavpn` | Mozilla VPN |
| `mozillavpn_backend_cirrus_live` | `mozillavpn_backend_cirrus` | Mozilla VPN backend Cirrus |
| `ads_backend_live` | `ads_backend` | Ads backend |
| `bedrock_live` | `bedrock` | Mozilla.org (Bedrock) |
| `mdn_yari_live` | `mdn_yari` | MDN Web Docs (Yari) |
| `mozphab_live` | `mozphab` | MozPhab code review tool |
| `sync_live` | `sync` | Firefox Sync |
| `glean_js_live` | `glean_js` | Glean.js (web SDK) |
| `glean_core_live` | `glean_core` | Glean core library |
| `engine_gecko_live` | `engine_gecko` | GeckoView engine |
| `lib_crash_live` | `lib_crash` | Android crash reporter component |
| `logins_store_live` | `logins_store` | Android logins storage |
| `android_places_live` | `android_places` | Android Places component |
| `rally_core_live` | `rally_core` | Firefox Rally core |
| `treeherder_live` | `treeherder` | Treeherder CI dashboard |

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
| `newtab` | 20–80 | Targeted or sectional depending on field count |
| `first_session` | 10–30 | Usually safe to request full schema |
| `deletion_request` | < 10 | Safe to request full schema |
| `crash` | 30–100 | Sectional or targeted |

---

## Alternate app_id Variations

Some apps changed their package name over time. If a URL returns 404, try these alternates:

| Preferred app_id | Alternate |
|---|---|
| `fenix` | `org_mozilla_fenix`, `org_mozilla_firefox_beta`, `org_mozilla_fenix_nightly` |
| `org_mozilla_firefox` | `fenix`, `org_mozilla_fenix` |
| `firefox_ios` | `org_mozilla_ios_firefox` |
| `org_mozilla_focus` | `focus_android` |
| `org_mozilla_klar` | `klar_android`, `org_mozilla_ios_klar` |

---

## Verification

If unsure whether an app_id is correct:
1. Visit https://dictionary.telemetry.mozilla.org/ and search for the app name
2. Browse to the app and find the table
3. Copy the URL — it contains the correct `app_id`

For a full list of all Glean apps and their BigQuery dataset families, fetch:
```
https://probeinfo.telemetry.mozilla.org/glean/repositories
```
Each entry has `app_id` (hyphenated, for probeinfo API) and `moz_pipeline_metadata_defaults.bq_dataset_family` (underscored, matches the BigQuery dataset minus `_live`/`_stable`).
