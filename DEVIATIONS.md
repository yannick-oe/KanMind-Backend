# Deviations

Deliberate deviations from the standard defaults, each dated with a
reason, the consequence and a rollback path. Precedence for these
decisions: endpoint documentation > frontend behaviour > checklist >
coding standards.

## 2026-07-23 — Django password validators are not applied

**Decision:** The registration flow does not run Django's
`AUTH_PASSWORD_VALIDATORS`, and the setting is removed from
`core/settings.py` so no validation is applied by the API, the admin
or `createsuperuser` either.

**Reason:** The endpoint contract for `POST /api/registration/` lists
only the fields `fullname`, `email`, `password`, `repeated_password`
and the error case `400 on invalid data`. Password-strength rules are
not part of the contract; the delivered frontend enforces its own
rules client-side. Applying server-side validators would reject
payloads the contract accepts and would block the fixed guest
password `asdasdasd`
(`docs/KanMind-Frontend-Vertragsfakten.md:22`).

**Consequence:** Weak passwords are accepted everywhere, including
`createsuperuser`. Acceptable for this project; the operator chooses
superuser and guest passwords manually.

**Rollback:** Re-add the `AUTH_PASSWORD_VALIDATORS` block to
`core/settings.py` and, if per-endpoint validation is wanted, call
`django.contrib.auth.password_validation.validate_password` inside
`RegistrationSerializer.validate`.

## 2026-07-23 — `fullname` is not required to contain two words

**Decision:** `RegistrationSerializer` accepts any non-empty
`fullname`; it does not require two space-separated words.

**Reason:** The two-word rule is not in the endpoint contract. It is a
frontend concern: `getInitials()` reads `parts[1][0]` unchecked and
throws for a single-word name
(`docs/KanMind-Frontend-Vertragsfakten.md:139-156`). The frontend
already enforces the rule client-side; a server-side rule would be an
undocumented extra constraint.

**Consequence:** A single-word `fullname` can be registered via the
API and would break `getInitials()` in the delivered frontend. Users
created by us (guest user, superusers, fixtures) are given a
two-word `fullname` to avoid this.

**Rollback:** Add `validate_fullname` to `RegistrationSerializer`
enforcing at least two words.

## 2026-07-24 — `POST /api/tasks/` allows the board owner, not only members

**Decision:** Creating a task is permitted for the board **owner OR a
member** of the board, implemented in `TaskCreateView._resolve_board`
via `user_is_board_participant`.

**Reason:** The endpoint documentation says the requester "must be a
member of the board". In this implementation the owner is **not**
automatically a member (`POST /api/boards/` does not auto-add the
owner — see the board scope). A strict "member only" reading would
stop an owner from creating tasks on their own board, which breaks the
delivered frontend. Owner-or-member is the reading that keeps the
frontend working and matches how every other board endpoint treats
access.

**Consequence:** A board owner who is not in the `members` list can
still create tasks on that board. This is broader than a literal
reading of the documentation, but consistent with the board endpoints.

**Rollback:** In `TaskCreateView._resolve_board`, replace
`user_is_board_participant` with a members-only check
(`board.members.filter(pk=request.user.id).exists()`).
