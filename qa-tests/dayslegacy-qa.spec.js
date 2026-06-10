const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const BASE = 'http://localhost:8000';
const DEMO_URL = `${BASE}/dashboard?demo=1`;
const ADMIN_PASSWORD = 'DL-QA-2026!Secure#Beta';
const REPORT_DIR = path.join(__dirname, 'report');
if (!fs.existsSync(REPORT_DIR)) fs.mkdirSync(REPORT_DIR, { recursive: true });

// Helper : capture + log console
async function capturePage(page, name) {
  await page.screenshot({ path: path.join(REPORT_DIR, `${name}-desktop.png`), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(REPORT_DIR, `${name}-mobile.png`), fullPage: true });
  await page.setViewportSize({ width: 1280, height: 720 });
}

async function getConsoleErrors(page) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(`PAGEERROR: ${err.message}`));
  return errors;
}

async function getNetworkIssues(page) {
  const issues = [];
  page.on('response', resp => {
    const status = resp.status();
    const url = resp.url();
    if (status >= 400 && !url.includes('favicon')) {
      issues.push(`${status} ${url}`);
    }
  });
  return issues;
}

// ============================================================
// TEST 1 : Racine /
// ============================================================
test('1. Ouvrir / redirige vers dashboard', async ({ page }) => {
  const consoleErrors = [];
  const networkIssues = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(`PAGEERROR: ${err.message}`));
  page.on('response', resp => { if (resp.status() >= 400) networkIssues.push(`${resp.status()} ${resp.url()}`); });

  await page.goto(`${BASE}/`);
  await page.waitForLoadState('networkidle');
  // Le backend sert dashboard.html sur / sans redirect — on vérifie le contenu
  await expect(page.locator('#login .l-brand-big')).toBeVisible();
  await capturePage(page, '01-root');

  fs.writeFileSync(path.join(REPORT_DIR, '01-console.txt'), consoleErrors.join('\n') || 'Aucune erreur console');
  fs.writeFileSync(path.join(REPORT_DIR, '01-network.txt'), networkIssues.join('\n') || 'Aucune erreur réseau');
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toHaveLength(0);
});

// ============================================================
// TEST 2 : /dashboard (login)
// ============================================================
test('2. Ouvrir /dashboard affiche login', async ({ page }) => {
  const consoleErrors = [];
  const networkIssues = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(`PAGEERROR: ${err.message}`));
  page.on('response', resp => { if (resp.status() >= 400) networkIssues.push(`${resp.status()} ${resp.url()}`); });

  await page.goto(`${BASE}/dashboard`);
  await page.waitForSelector('#login', { timeout: 5000 });
  await expect(page.locator('.l-brand-big')).toContainText('Days Legacy');
  await expect(page.locator('.l-sophia-name')).toContainText('Sophia');
  await capturePage(page, '02-dashboard-login');

  fs.writeFileSync(path.join(REPORT_DIR, '02-console.txt'), consoleErrors.join('\n') || 'Aucune erreur console');
  fs.writeFileSync(path.join(REPORT_DIR, '02-network.txt'), networkIssues.join('\n') || 'Aucune erreur réseau');
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toHaveLength(0);
});

// ============================================================
// TEST 3 : Mode démo ?demo=1
// ============================================================
test('3. Mode démo ?demo=1 — bypass auth + données visibles', async ({ page }) => {
  const consoleErrors = [];
  const networkIssues = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(`PAGEERROR: ${err.message}`));
  page.on('response', resp => { if (resp.status() >= 400) networkIssues.push(`${resp.status()} ${resp.url()}`); });

  await page.goto(DEMO_URL);
  await page.waitForSelector('#app', { timeout: 5000 });

  // Vérifie que le login est caché
  const loginDisplay = await page.locator('#login').evaluate(el => getComputedStyle(el).display);
  expect(loginDisplay).toBe('none');

  // Vérifie le pill DÉMO
  await expect(page.locator('#mode-txt')).toContainText('DÉMO');

  // Vérifie les prospects démo (5 cartes)
  const cards = page.locator('#p-grid .p-card');
  await expect(cards).toHaveCount(5);

  // Vérifie signaux marché
  const signals = page.locator('#signals-list .sig-item');
  await expect(signals).toHaveCount(5);

  // Vérifie tableau leads
  const rows = page.locator('#tbody tr');
  await expect(rows).toHaveCount(5);

  await capturePage(page, '03-demo-mode');

  fs.writeFileSync(path.join(REPORT_DIR, '03-console.txt'), consoleErrors.join('\n') || 'Aucune erreur console');
  fs.writeFileSync(path.join(REPORT_DIR, '03-network.txt'), networkIssues.join('\n') || 'Aucune erreur réseau');
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toHaveLength(0);
});

// ============================================================
// TEST 4 : Login réel
// ============================================================
test('4. Login réel avec mot de passe fort', async ({ page }) => {
  const consoleErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(`PAGEERROR: ${err.message}`));

  await page.goto(`${BASE}/dashboard`);
  await page.fill('#pw', ADMIN_PASSWORD);
  await page.click('.l-btn');
  await page.waitForSelector('#app', { timeout: 5000 });

  // Vérifie mode PROD
  await expect(page.locator('#mode-txt')).toContainText('PROD');

  // Vérifie que le tableau est vide (pas de leads réels en base QA)
  await expect(page.locator('#tbody')).toContainText('Aucun prospect enregistré');

  await capturePage(page, '04-login-real');

  fs.writeFileSync(path.join(REPORT_DIR, '04-console.txt'), consoleErrors.join('\n') || 'Aucune erreur console');
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toHaveLength(0);
});

// ============================================================
// TEST 5 : Navigation onglets Pipeline / Audits
// ============================================================
test('5. Navigation onglets Pipeline + Audits Clients', async ({ page }) => {
  await page.goto(DEMO_URL);
  await page.waitForSelector('#app', { timeout: 5000 });

  // Pipeline actif par défaut
  await expect(page.locator('#tab-pipeline')).toHaveClass(/active/);
  await expect(page.locator('#tab-audits')).not.toHaveClass(/active/);

  // Clique sur Audits
  await page.click('.nav-tab[data-tab="audits"]');
  await expect(page.locator('#tab-audits')).toHaveClass(/active/);
  await expect(page.locator('#tab-pipeline')).not.toHaveClass(/active/);

  // Vérifie contenu YAWatch
  await expect(page.locator('.audit-h-title')).toContainText('YAWatch Industries');
  await expect(page.locator('#audit-score')).toContainText('7.8');
  const findings = page.locator('.finding-card');
  await expect(findings).toHaveCount(6);

  await capturePage(page, '05-tab-audits');
});

// ============================================================
// TEST 6 : Toggle Démo/Prod
// ============================================================
test('6. Toggle Démo/Prod ne casse rien', async ({ page }) => {
  await page.goto(DEMO_URL);
  await page.waitForSelector('#app', { timeout: 5000 });

  // Démo -> Prod (retourne au login)
  await page.click('#mode-pill');
  await page.waitForSelector('#login', { timeout: 5000 });
  await expect(page.locator('#login')).toBeVisible();

  // Login et repasse en démo
  await page.fill('#pw', ADMIN_PASSWORD);
  await page.click('.l-btn');
  await page.waitForSelector('#app', { timeout: 5000 });
  await page.click('#mode-pill');
  await page.waitForSelector('#app', { timeout: 5000 });
  await expect(page.locator('#mode-txt')).toContainText('DÉMO');

  await capturePage(page, '06-toggle-mode');
});

// ============================================================
// TEST 7 : Sophia répond en démo (mock) ou erreur propre
// ============================================================
test('7. Sophia répond en mode démo (mock)', async ({ page }) => {
  await page.goto(DEMO_URL);
  await page.waitForSelector('#app', { timeout: 5000 });

  await page.fill('#sophia-q', 'Bilan de la semaine');
  await page.click('#sophia-btn');

  // Attend la réponse
  await page.waitForSelector('#sophia-resp.show', { timeout: 10000 });
  const respText = await page.locator('#sophia-resp').textContent();

  // Vérifie que la réponse contient du texte et le disclaimer
  expect(respText.length).toBeGreaterThan(50);
  expect(respText).toContain('Disclaimer');

  await capturePage(page, '07-sophia-mock');
});

// ============================================================
// TEST 8 : Console 0 erreur critique
// ============================================================
test('8. Console navigateur : 0 erreur critique', async ({ page }) => {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(`PAGEERROR: ${err.message}`));

  await page.goto(DEMO_URL);
  await page.waitForTimeout(3000);
  // Navigue un peu
  await page.click('.nav-tab[data-tab="audits"]');
  await page.waitForTimeout(1000);
  await page.click('.nav-tab[data-tab="pipeline"]');
  await page.waitForTimeout(1000);

  const filtered = errors.filter(e => !e.includes('favicon') && !e.includes('SpeechRecognition') && !e.includes('webkitSpeechRecognition'));
  fs.writeFileSync(path.join(REPORT_DIR, '08-console-all.txt'), filtered.join('\n') || 'Aucune erreur critique');
  expect(filtered).toHaveLength(0);
});

// ============================================================
// TEST 9 : Réseau pas de 404/500 inattendu
// ============================================================
test('9. Réseau : pas de 404/500 inattendu', async ({ page }) => {
  const issues = [];
  page.on('response', resp => {
    const status = resp.status();
    const url = resp.url();
    // Ignore les favicon et les requêtes externes (fontshare, etc.)
    if (status >= 400 && !url.includes('favicon') && url.includes('localhost:8000')) {
      issues.push(`${status} ${url}`);
    }
  });

  await page.goto(DEMO_URL);
  await page.waitForTimeout(3000);
  await page.click('.nav-tab[data-tab="audits"]');
  await page.waitForTimeout(1000);

  fs.writeFileSync(path.join(REPORT_DIR, '09-network-all.txt'), issues.join('\n') || 'Aucune erreur réseau');
  expect(issues).toHaveLength(0);
});

// ============================================================
// TEST 10 : Responsive mobile
// ============================================================
test('10. Responsive mobile — iPhone + Android viewport', async ({ page }) => {
  // iPhone 13
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(DEMO_URL);
  await page.waitForSelector('#app', { timeout: 5000 });
  await page.screenshot({ path: path.join(REPORT_DIR, '10-responsive-iphone.png'), fullPage: true });

  // Vérifie que les cartes passent en colonne
  const cards = page.locator('#p-grid .p-card');
  await expect(cards.first()).toBeVisible();

  // Android Pixel 7
  await page.setViewportSize({ width: 412, height: 915 });
  await page.reload();
  await page.waitForSelector('#app', { timeout: 5000 });
  await page.screenshot({ path: path.join(REPORT_DIR, '10-responsive-android.png'), fullPage: true });

  // Vérifie que Sophia est visible
  await expect(page.locator('.sophia-hero')).toBeVisible();
});
