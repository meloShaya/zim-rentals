# Zim Rentals API Playbook for Mobile Clients

This playbook distills everything Expo/React Native engineers need to integrate the v1 REST and WebSocket APIs.

---

## 1. Base Configuration
- **REST base URL** (Render / production): `https://homemarketplace.co.zw/api/v1/`
- **WebSocket base URL**: `wss://homemarketplace.co.zw/ws/`
- **Auth scheme**: Bearer tokens via JWT (SimpleJWT).
- **Pagination**: Page-number (`page`, `page_size`). Default size 10.
- **Date/Time**: ISO8601 UTC.
- **Content-Type**: `application/json` for requests (multipart for uploads).

### Environment helpers
```ts
export const API_BASE = 'https://homemarketplace.co.zw/api/v1';
export const WS_BASE = 'wss://homemarketplace.co.zw/ws';
```

---

## 2. Authentication & Profiles
| Endpoint | Method | Description |
| --- | --- | --- |
| `/auth/users/` | POST | Register user (landlord/renter) |
| `/auth/sessions/login/` | POST | Username/email + password → JWT pair |
| `/auth/sessions/logout/` | POST | Requires `refresh` token (blacklists) |
| `/auth/sessions/refresh/` | POST | Refresh token → new pair |
| `/users/` | GET | Current user (requires auth) |
| `/users/me/` | GET | Profile details |
| `/users/profile/` | PATCH | Update profile fields |
| `/users/avatar/` | POST | Upload profile image |

**Registration payload**
```json
{
  "username": "zimrenter",
  "email": "zim@rentals.com",
  "password": "Passw0rd!",
  "password_confirm": "Passw0rd!",
  "user_type": "renter",
  "phone_number": "+263771234567"
}
```

Store `access` token for API calls, `refresh` token securely (SecureStore / Keychain). Auto-refresh when 401 with expired signature.

---

## 3. Listings & Discovery
### Core resources
| Endpoint | Method | Notes |
| --- | --- | --- |
| `/listings/` | GET | Filtered search; landlords can POST |
| `/listings/{id}/` | GET | Detail |
| `/listings/{id}/favorite/` | POST/DELETE | Favorite/unfavorite |
| `/listings/mine/` | GET | Landlord’s listings |
| `/listings/popular/` | GET | Top listings by favorites |
| `/listings/{id}/analytics/` | GET | Stats (landlords only) |

### Query parameters (all optional)
- `search=<term>` (title/desc/suburb/city)
- `city`, `property_type`, `currency`
- `price_min`, `price_max`
- `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`
- `is_furnished`, `has_water`, `has_electricity`, `has_wifi`
- `ordering=<field>` — `created_at`, `price`, `bedrooms`

**Create listing payload (landlord)**
```json
{
  "title": "Cozy cottage",
  "description": "Two bedrooms, garden",
  "price": "350.00",
  "currency": "USD",
  "city": "harare",
  "suburb": "Avondale",
  "address": "15 Example Street",
  "property_type": "cottage",
  "bedrooms": 2,
  "bathrooms": 1,
  "is_furnished": true,
  "has_water": true,
  "has_electricity": true,
  "has_wifi": false,
  "phone_number": "+263771234567",
  "whatsapp_number": "+263771234567"
}
```
Upload listing images via `/listings/{id}/images/` (multipart with `image` file field).

### Favorites
- `GET /favorites/` – current user favorites
- `GET /listings/{listingId}/favorites/` – users who favorited listing

---

## 4. Roommate Finder
| Endpoint | Method | Description |
| --- | --- | --- |
| `/roommates/` | GET/POST | Browse/create profiles |
| `/roommates/me/` | GET | Retrieve own profile |
| `/roommates/{id}/` | PATCH/DELETE | Update/delete profile |
| `/roommates/{id}/connections/` | POST | Send request (message optional) |
| `/roommates/{id}/connections/{connectionId}/` | PATCH | Owner accepts/declines |

**Filters** (`GET /roommates/`): `city`, `gender`, `lifestyle`, `min_budget`, `max_budget`, `move_in_before`, `move_in_after`, `is_smoker`, `has_pets`.

---

## 5. Messaging & Realtime
### REST
| Endpoint | Method | Description |
| --- | --- | --- |
| `/listings/{listingId}/messages/` | GET/POST | Thread messages |
| `/listings/{listingId}/messages/{messageId}/mark-read/` | POST | Mark read |
| `/notifications/` | GET | System notifications (direct message listings) |
| `/notifications/mark-read/` | POST | Bulk mark read `{ "ids": [1,2] }` |

### WebSocket Channels
- `ws/rooms/{listingId}/` – chat messages (send/receive JSON)
  - Send message: `{ "type": "message", "message": "Is it available?" }`
  - Mark read: `{ "type": "mark_read", "message_id": 42 }`
  - Server broadcasts `message` and `read_status` payloads.
- `ws/notifications/` – user-specific notification stream. Requires authenticated session cookie or token integration (consider custom auth middleware if needed).

---

## 6. Saved Searches & Alerts
| Endpoint | Method | Description |
| --- | --- | --- |
| `/saved-searches/` | GET/POST | Manage alerts |
| `/saved-searches/{id}/` | PATCH/DELETE | Update/delete |
| `/saved-searches/{id}/toggle/` | POST | Enable/disable |
| `/saved-searches/{id}/matches/` | GET | Current matching listings |
| `/saved-searches/{id}/alerts/` | GET | Listings for saved search (same as matches) |

Payload mirrors UI filters. Each record includes `match_count` for quick UX hints.

---

## 7. Landlord Verification
| Endpoint | Method | Description |
| --- | --- | --- |
| `/verifications/` | POST | Upload landlord documents (file field `document`) |
| `/verifications/` | GET | Landlord history |
| `/verifications/{id}/admin_update/` | PATCH | Staff: approve/reject, add notes |

When a verification is approved, the user’s `is_verified_landlord` flag updates automatically.

---

## 8. Metadata Helper
- `GET /metadata/` → returns enumerations for property types, cities, roommate genders, lifestyles. Useful for populating filters without hardcoding.

Example response:
```json
{
  "property_types": [{"value": "house", "label": "House"}, ...],
  "listing_cities": [{"value": "harare", "label": "Harare"}],
  "roommate_lifestyles": [...],
  "roommate_genders": [...]
}
```

---

## 9. Error Handling & Status Codes
- `400` validation errors – expect `{ "field": ["message"] }` structure.
- `403` forbidden – unauthorized landlord actions / roommate restrictions.
- `404` – missing resources.
- `429` – defined throttles: anonymous `100/day`, authenticated `1000/day`.

### Rate limiting UI tips
Implement exponential backoff or user messaging when `429` occurs. Reset occurs daily.

---

## 10. Performance & Offline Guidance
- Cache metadata and lookup lists locally.
- Use pagination + infinite scroll for listing/roommate feeds (`page` param).
- For uploads (images/documents) use background tasks and progress spinners.
- Consider optimistic UI for favorites and chat messages; reconcile via WebSocket events.
- Leverage `saved-searches/{id}/matches/` to prefetch results when push notification arrives.

---

## 11. Testing
Use the existing pytest suite as reference. For mobile mock servers, reproduce key flows:
1. Auth → create listing → favorite → message.
2. Roommate connection lifecycle.
3. Verification submission/approval.

Run locally with:
```bash
pytest api/tests -q
```

---

## 12. Future Enhancements (Roadmap hooks)
- Attachments in chat (binary uploads)
- Booking workflows (settings flag `ENABLE_BOOKINGS`)
- Push notification hooks (integrate FCM/APNs via `/notifications/` feed)
- Metrics endpoints (analytics expansion)

---

### Contact
For API questions: meloshaya02@gmail.com.
