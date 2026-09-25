# Notification System — Django + React

An admin manages every notification from one screen. No need to open WhatsApp, Postmark or OneSignal to create templates — creating, editing, toggling and test-sending all happen in the admin panel.

```
notification-system/
├── backend/           Django + DRF   → deploy on Render
├── frontend/          React + Vite   → deploy on Vercel
└── SETUP_GUIDE.pdf    full install / run / test guide
```

## What is built

| Feature | Status |
|---|---|
| Trigger CRUD (rows of the admin table) | Done |
| Template CRUD per channel (cells) | Done |
| WhatsApp Cloud API (sandbox) | Done |
| Email — Postmark / Brevo / Resend / console | Done (`EMAIL_PROVIDER` switches) |
| Web Push — OneSignal, browser only | Done |
| On/off toggle per cell | Done |
| Test send per cell | Done |
| Variable mapping `{{name}}`, `{{email}}`, … | Done |
| Login / Logout / Signup triggers fire automatically | Done |
| Not logged in 1 day / 1 week (cron) | Done |
| Delivery log screen | Done |

## Backend (local)

Use Python 3.12 (3.14 has no prebuilt wheels for some packages yet).

```bash
cd backend
py -3.12 -m venv venv          
venv\Scripts\activate          
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_triggers
python manage.py runserver
```

Runs at `http://127.0.0.1:8000`. `seed_triggers` creates the triggers, sample templates and the admin account **admin / admin12345** (override with `ADMIN_USERNAME` / `ADMIN_PASSWORD`).

Local development uses SQLite. PostgreSQL (psycopg 3) is installed on Render only, through `requirements-prod.txt`.

### Environment variables

```
SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, DATABASE_URL
WHATSAPP_ACCESS_TOKEN, PHONE_NUMBER_ID, WHATSAPP_API_VERSION
EMAIL_PROVIDER=postmark|brevo|resend|console
POSTMARKAPP_TOKEN, POSTMARK_FROM_EMAIL, BREVO_API_KEY, RESEND_API_KEY
ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY
CRON_SECRET
```

Set `EMAIL_PROVIDER=console` to test the whole flow without any API key — the email is printed in the server terminal.

## Frontend (local)

```bash
cd frontend
npm install
cp .env.example .env     # VITE_API_BASE + VITE_ONESIGNAL_APP_ID
npm run dev
```

Runs at `http://localhost:5173`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register/` | New user, fires `signup` |
| POST | `/api/auth/login/` | Sign in, fires `login` |
| POST | `/api/auth/logout/` | Sign out, fires `logout` |
| GET/PATCH | `/api/auth/me/` | Profile (phone, email) |
| GET/POST | `/api/triggers/` | List / create triggers (admin) |
| PATCH/DELETE | `/api/triggers/{id}/` | Edit / delete |
| POST | `/api/triggers/{id}/fire/` | Fire manually (demo) |
| GET/POST | `/api/templates/` | List / create templates |
| PATCH/DELETE | `/api/templates/{id}/` | Edit / delete |
| POST | `/api/templates/{id}/toggle/` | Channel on/off |
| POST | `/api/templates/{id}/test-send/` | Send a test message |
| GET | `/api/logs/` | Delivery log |
| POST | `/api/push/subscribe/` | Save browser subscription |
| POST | `/api/triggers-fire/{code}/` | Fire any custom trigger |
| GET/POST | `/api/cron/inactivity/?secret=…` | Inactive-user check |

Auth header: `Authorization: Token <token>`.

## Sandbox accounts

**WhatsApp** — developers.facebook.com → app → WhatsApp product → API Setup gives a test number and a temporary token. Add your own number to the recipient list. The token expires in about a day; generate a new one when sends fail.

**Email** — Postmark (~100/month), Brevo (300/day, the easiest for this assignment), Resend (3,000/month), Mailgun or SES. Verify the sender, put the API key in `.env` and set `EMAIL_PROVIDER`.

**Web Push** — onesignal.com → website app → Web Push only. `VITE_ONESIGNAL_APP_ID` on the frontend, `ONESIGNAL_APP_ID` + `ONESIGNAL_REST_API_KEY` on the backend.

Never commit `.env`.

## Deploy

**Render (backend):** build command `./build.sh`, start command `gunicorn config.wsgi:application`. Set every env var, with `DEBUG=False`, `ALLOWED_HOSTS=.onrender.com` and `CORS_ALLOWED_ORIGINS=https://<your-app>.vercel.app`. Add a daily cron job hitting `/api/cron/inactivity/?secret=<CRON_SECRET>`.

**Vercel (frontend):** import the folder (framework Vite), set `VITE_API_BASE` and `VITE_ONESIGNAL_APP_ID`. `vercel.json` handles SPA routing.

## Using the admin panel

1. Sign in as **admin / admin12345**.
2. Open **Notification settings** — rows are triggers, columns are WhatsApp / Email / Web Push.
3. In a cell choose **Create template**, write the message (variables such as `{{name}}` are supported), then **Save template**.
4. **Send test** delivers it to your phone, inbox or browser.
5. The toggle turns a channel on or off; **Fire now** runs the whole row.
6. **Delivery log** records every attempt with its result.

User flow: `/register` → save phone and email → **Turn on browser notifications** → sign out and back in to receive the notifications.

## Task D answers

**1. What is a trigger? Three examples.**
A trigger is any event or condition on the website that should cause a notification to be sent. Examples: a user places an order, a user requests a password reset, a user has not visited for seven days. Login and logout are just two common examples.

**2. What are the three channels?**
WhatsApp (a message through the WhatsApp Cloud API), Email (through Postmark or another free transactional email API), and Web Push (a pop-up notification in the browser).

**3. Why create templates in the admin panel instead of on the Postmark or WhatsApp site?**
Because the admin sees and controls everything in one place. No logging into separate provider dashboards, message text is changed in one screen, a channel is switched off with one click, and the mapping of which trigger sends what on which channel is visible as a single table. The provider API tokens stay on the backend, which is safer, and switching provider does not change the admin workflow.

**4. What is Web Push?**
A notification delivered through the browser. The user allows notifications once, the browser is subscribed, and after that the site can send a pop-up notification even when the page is closed. It is not mobile app push — browser only.

## Where things live

| Assignment item | File |
|---|---|
| Admin APIs for triggers and templates | `backend/notifications/views.py` |
| WhatsApp / Email / Web Push integration | `backend/notifications/services/` |
| Sending when a trigger fires | `backend/notifications/dispatcher.py` |
| Toggles and variable mapping storage | `backend/notifications/models.py` |
| User website (login, logout) | `frontend/src/pages/Login.jsx`, `Dashboard.jsx` |
| Admin table (rows × channels) | `frontend/src/pages/AdminNotifications.jsx` |
| Create / edit / test / toggle | `frontend/src/components/TemplateModal.jsx` |
| Web Push subscribe | `frontend/src/components/PushSubscribe.jsx` |
| Two triggers on three channels | `seed_triggers` command |
