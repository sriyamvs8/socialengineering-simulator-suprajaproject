// server.js
// Backend for the Teady Login Dashboard.
// Reads directly from database.db (schema: users, login_history) and
// exposes read-only JSON endpoints the frontend polls for live updates.

const path = require('path');
const express = require('express');
const Database = require('better-sqlite3');

const DB_PATH = process.env.DB_PATH || path.join(__dirname, 'database.db');
const PORT = process.env.PORT || 3001;

const db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
// Note: journal_mode is not set here because it requires a writable handle.
// If your app's own write connection already uses WAL mode (recommended for
// an app that writes logins while this dashboard reads), reads here will
// see committed rows without any extra config needed.

const app = express();
app.use(express.static(path.join(__dirname, 'public')));

// ---- Queries -----------------------------------------------------------
// All computed fresh on every request. For a table with thousands of rows
// this is instant with SQLite + indexes; no caching layer needed at this scale.

function getStats() {
  const totalUsers = db.prepare(`SELECT COUNT(*) AS n FROM users`).get().n;
  const totalLogins = db.prepare(`SELECT COUNT(*) AS n FROM login_history`).get().n;

  const loginsPerDay = db.prepare(`
    SELECT date(login_time) AS day, COUNT(*) AS count
    FROM login_history
    GROUP BY day
    ORDER BY day ASC
  `).all();

  const loginsPerWeek = db.prepare(`
    SELECT strftime('%Y-W%W', login_time) AS week, COUNT(*) AS count
    FROM login_history
    GROUP BY week
    ORDER BY week ASC
  `).all();

  // Hour of day, 0-23, zero-filled so the chart never has gaps
  const hourRows = db.prepare(`
    SELECT CAST(strftime('%H', login_time) AS INTEGER) AS hour, COUNT(*) AS count
    FROM login_history
    GROUP BY hour
  `).all();
  const byHour = Array.from({ length: 24 }, (_, h) => {
    const found = hourRows.find(r => r.hour === h);
    return { hour: h, count: found ? found.count : 0 };
  });

  // Day of week, 0=Sunday .. 6=Saturday, zero-filled
  const dowNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dowRows = db.prepare(`
    SELECT CAST(strftime('%w', login_time) AS INTEGER) AS dow, COUNT(*) AS count
    FROM login_history
    GROUP BY dow
  `).all();
  const byDayOfWeek = dowNames.map((name, i) => {
    const found = dowRows.find(r => r.dow === i);
    return { day: name, count: found ? found.count : 0 };
  });

  const topUsers = db.prepare(`
    SELECT email, COUNT(*) AS count
    FROM login_history
    GROUP BY email
    ORDER BY count DESC
    LIMIT 10
  `).all();

  // New vs returning: a login is "new" if it's the earliest login_history
  // row for that email (i.e. their first ever recorded login).
  const newVsReturning = db.prepare(`
    WITH ranked AS (
      SELECT id,
             ROW_NUMBER() OVER (PARTITION BY email ORDER BY login_time ASC, id ASC) AS rn
      FROM login_history
    )
    SELECT
      SUM(CASE WHEN rn = 1 THEN 1 ELSE 0 END) AS new_logins,
      SUM(CASE WHEN rn > 1 THEN 1 ELSE 0 END) AS returning_logins
    FROM ranked
  `).get();

  const avgLoginsPerUser = db.prepare(`
    SELECT AVG(cnt) AS avg FROM (
      SELECT COUNT(*) AS cnt FROM login_history GROUP BY email
    )
  `).get().avg;

  const recentLogins = db.prepare(`
    SELECT id, email, login_time
    FROM login_history
    ORDER BY login_time DESC, id DESC
    LIMIT 25
  `).all();

  // Lets the frontend cheaply detect "is there anything new" without
  // re-rendering everything: latest id + row count is enough of a fingerprint.
  const latest = db.prepare(`
    SELECT COALESCE(MAX(id), 0) AS maxId, COUNT(*) AS n FROM login_history
  `).get();

  return {
    totalUsers,
    totalLogins,
    loginsPerDay,
    loginsPerWeek,
    byHour,
    byDayOfWeek,
    topUsers,
    newLogins: newVsReturning.new_logins || 0,
    returningLogins: newVsReturning.returning_logins || 0,
    avgLoginsPerUser: avgLoginsPerUser || 0,
    recentLogins,
    fingerprint: `${latest.maxId}-${latest.n}`,
    generatedAt: new Date().toISOString(),
  };
}

// ---- Routes --------------------------------------------------------------

app.get('/api/stats', (req, res) => {
  try {
    res.json(getStats());
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to read stats', detail: err.message });
  }
});

// Lightweight endpoint the frontend polls frequently to know whether a
// full refresh is worth doing, without paying the cost of every query above.
app.get('/api/heartbeat', (req, res) => {
  try {
    const latest = db.prepare(`
      SELECT COALESCE(MAX(id), 0) AS maxId, COUNT(*) AS n FROM login_history
    `).get();
    res.json({ fingerprint: `${latest.maxId}-${latest.n}` });
  } catch (err) {
    res.status(500).json({ error: 'Failed to read heartbeat', detail: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Login dashboard backend running at http://localhost:${PORT}`);
  console.log(`Reading from: ${DB_PATH}`);
});
