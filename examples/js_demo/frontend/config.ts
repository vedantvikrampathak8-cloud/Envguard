// examples/js_demo/frontend/config.ts
// A Vite + React frontend using import.meta.env (the Vite convention).

// -------------------------------------------------------------------
// Vite exposes env vars via import.meta.env (VITE_ prefix convention)
// -------------------------------------------------------------------
const API_BASE_URL    = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:3000'
const APP_TITLE       = import.meta.env.VITE_APP_TITLE    ?? 'My App'
const SENTRY_DSN      = import.meta.env.VITE_SENTRY_DSN           // required
const ANALYTICS_KEY   = import.meta.env.VITE_ANALYTICS_KEY        // required
const FEATURE_DARK_MODE = import.meta.env.VITE_FEATURE_DARK_MODE ?? 'true'

export const config = {
  apiBaseUrl:    API_BASE_URL,
  appTitle:      APP_TITLE,
  sentryDsn:     SENTRY_DSN,
  analyticsKey:  ANALYTICS_KEY,
  featureDarkMode: FEATURE_DARK_MODE === 'true',
}
