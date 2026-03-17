// examples/js_demo/server.js
// A fake Express-style server using various process.env patterns.
// Run `envguard scan examples/js_demo -l javascript` to see envguard in action.

const express = require('express')

// -------------------------------------------------------------------
// Core config — bracket and dot access
// -------------------------------------------------------------------
const PORT       = parseInt(process.env.PORT ?? '3000')
const NODE_ENV   = process.env.NODE_ENV ?? 'development'
const LOG_LEVEL  = process.env.LOG_LEVEL || 'info'

// -------------------------------------------------------------------
// Database
// -------------------------------------------------------------------
const DATABASE_URL = process.env['DATABASE_URL']                 // required
const DB_POOL_MIN  = parseInt(process.env.DB_POOL_MIN ?? '2')
const DB_POOL_MAX  = parseInt(process.env.DB_POOL_MAX ?? '10')

// -------------------------------------------------------------------
// Auth & secrets
// -------------------------------------------------------------------
const JWT_SECRET    = process.env.JWT_SECRET                     // required
const JWT_EXPIRES   = process.env.JWT_EXPIRES_IN ?? '7d'
const SESSION_SECRET = process.env.SESSION_SECRET                // required

// -------------------------------------------------------------------
// External services
// -------------------------------------------------------------------
const STRIPE_SECRET_KEY    = process.env.STRIPE_SECRET_KEY       // required
const STRIPE_WEBHOOK_SECRET = process.env['STRIPE_WEBHOOK_SECRET'] // required
const SENDGRID_API_KEY     = process.env.SENDGRID_API_KEY        // required
const SENDGRID_FROM_EMAIL  = process.env.SENDGRID_FROM_EMAIL ?? 'noreply@example.com'

// -------------------------------------------------------------------
// AWS / storage
// -------------------------------------------------------------------
const { AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION } = process.env
const S3_BUCKET = process.env.S3_BUCKET                          // required

// -------------------------------------------------------------------
// Feature flags
// -------------------------------------------------------------------
const ENABLE_RATE_LIMIT = process.env.ENABLE_RATE_LIMIT ?? 'true'
const MAINTENANCE_MODE  = process.env.MAINTENANCE_MODE  ?? 'false'
const CORS_ORIGIN       = process.env.CORS_ORIGIN       || 'http://localhost:3000'
