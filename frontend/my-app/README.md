# E-Learning Frontend — Authentication

Covers every auth endpoint you listed. A few things are marked below as
**needs verifying against your actual backend** - I built this from the
API list alone, and a couple of details (exact response field names,
Djoser URL patterns) depend on your specific `DJOSER` settings, which I
haven't seen directly.

## Setup

    npm install
    npm run dev

Runs at http://localhost:3000. Set `VITE_API_URL` in `.env.local` to
match your backend (default: http://localhost:8000).

## Endpoint coverage

| Feature | Frontend file | Backend endpoint |
|---|---|---|
| Register | `pages/Register.jsx` | `POST /{lang}/auth/users/` |
| Activate email | `pages/ActivateAccount.jsx` | `POST /{lang}/auth/users/activation/` |
| Login | `pages/Login.jsx` | `POST /{lang}/auth/token/login/` |
| Logout | `context/AuthContext.jsx` | `POST /{lang}/auth/token/logout/` |
| Enable 2FA | `components/TwoFactorSetup.jsx` | `POST /{lang}/api/admin/set-two-factor-auth/` |
| Verify 2FA | `components/TwoFactorSetup.jsx` | `POST /{lang}/api/admin/verify-two-factor-auth/` |
| Request password reset | `pages/ForgotPassword.jsx` | `POST /{lang}/auth/users/reset_password/` |
| Confirm password reset | `pages/ResetPasswordConfirm.jsx` | `POST /{lang}/auth/users/reset_password_confirm/` |
| Google OAuth start | `context/AuthContext.jsx` (`loginWithGoogle`) | `GET /{lang}/auth/o/google-oauth2/?redirect_uri=...` |
| Google OAuth finish | `pages/GoogleCallback.jsx` | `GET /{lang}/auth/o/google-oauth2/?state=...&code=...` |
| Current user | `context/AuthContext.jsx` (`fetchCurrentUser`) | `GET /{lang}/auth/users/me/` |

## Important: Token auth, not JWT

This backend uses Djoser's **TokenAuthentication**, not JWT. The header
format is `Authorization: Token <key>`, not `Authorization: Bearer <key>`.
This is handled in `api/client.js` - just flagging it since it's a real,
easy mistake to copy from a JWT-based project (like the expense tracker)
without noticing the scheme is different.

## Things to verify against your actual backend

1. **Register field names** (`Register.jsx`) - currently sends
   `email`, `password`, `re_password`. If your `UserCreateSerializer`
   requires more fields (first_name, last_name, role selection, etc.),
   add them to the form.

2. **Activation/reset URL patterns** (`ActivateAccount.jsx`,
   `ResetPasswordConfirm.jsx`) - the route params `:uid/:token` must
   match your backend's `DJOSER['ACTIVATION_URL']` and
   `DJOSER['PASSWORD_RESET_CONFIRM_URL']` settings exactly, since
   that's what determines the link the email actually contains. Check
   `settings.py` for these values and adjust the React Router paths in
   `App.jsx` to match if they differ from `activate/:uid/:token` and
   `password/reset/confirm/:uid/:token`.

3. **2FA response shape** (`TwoFactorSetup.jsx`) - assumes the
   `set-two-factor-auth` endpoint returns `{ "qr_code": "..." }` as
   either a base64 PNG or a data URI. Check the actual response shape
   and adjust `data.qr_code` if the field is named differently.

4. **Login payload field** - assumes login takes `email` (matching a
   CustomUser with `USERNAME_FIELD = "email"`). If it's actually
   `username`, change the payload key in `AuthContext.jsx`'s `login()`.

5. **Google OAuth response** (`completeGoogleLogin`) - assumes the
   callback returns an auth token under `auth_token`, `access_token`,
   or `key` (tried in that order). Check the real response and simplify
   once confirmed.
