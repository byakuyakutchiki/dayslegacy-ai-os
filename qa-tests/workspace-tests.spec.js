const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const WS_URL = 'http://localhost:8000/workspace?demo=1';
const REPORT_DIR = path.join(__dirname, 'report');
if (!fs.existsSync(REPORT_DIR)) fs.mkdirSync(REPORT_DIR, { recursive: true });

// ============================================================
// TEST 11 : Workspace demo — layout complet visible
// ============================================================
test('11. Workspace demo — layout sidebar + centre + Sophia', async ({ page }) => {
  page.on('pageerror', err => console.log('PAGEERROR:', err.message));
  page.on('response', resp => { if (resp.status() >= 400) console.log('HTTP', resp.status(), resp.url()); });

  await page.goto(WS_URL);
  await page.waitForSelector('#app.active', { timeout: 5000 });

  // Capture desktop
  await page.screenshot({ path: path.join(REPORT_DIR, '11-workspace-desktop.png'), fullPage: true });

  // Sidebar : workspaces selector + rooms + members
  await expect(page.locator('#ws-select')).toBeVisible();
  await expect(page.locator('#room-list .room-item')).toHaveCount(3); // DEMO_ROOMS pour ws=1
  await expect(page.locator('#member-list .member-item')).toHaveCount(3);

  // Centre : zone réunion + chat + documents
  await expect(page.locator('#room-title')).toContainText('Sélectionnez une salle');
  await expect(page.locator('#visio-badge')).toContainText('Module visio en préparation');
  await expect(page.locator('#chat-messages')).toBeVisible();
  await expect(page.locator('#doc-grid')).toBeVisible();

  // Panel droit : Sophia
  await expect(page.locator('#rightpanel')).toBeVisible();
  await expect(page.locator('#sophia-resp')).toBeVisible();

  // Capture mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await page.waitForSelector('#app.active', { timeout: 5000 });
  await page.screenshot({ path: path.join(REPORT_DIR, '11-workspace-mobile.png'), fullPage: true });
});

// ============================================================
// TEST 12 : Workspace — sélection salle + messages + envoi
// ============================================================
test('12. Workspace — sélection salle et chat fonctionnel', async ({ page }) => {
  await page.goto(WS_URL);
  await page.waitForSelector('#app.active', { timeout: 5000 });

  // Sélectionner la première salle
  await page.click('#room-list .room-item:first-child');
  await page.waitForTimeout(300);

  // Vérifie que le titre de la salle s'affiche
  await expect(page.locator('#room-title')).toContainText('Salle Iris');

  // Vérifie que les messages apparaissent
  const msgs = page.locator('#chat-messages .msg');
  await expect(msgs).toHaveCount(3);

  // Envoie un message
  await page.fill('#chat-input', 'Test QA message');
  await page.click('#chat-messages + .chat-input-wrap .btn-gold'); // bouton Envoyer
  await page.waitForTimeout(500);

  // Le message doit apparaître
  await expect(page.locator('#chat-messages .msg')).toHaveCount(4);

  // Capture
  await page.screenshot({ path: path.join(REPORT_DIR, '12-workspace-chat.png'), fullPage: true });
});

// ============================================================
// TEST 13 : Workspace responsive tablette + mobile
// ============================================================
test('13. Workspace responsive — tablette + mobile', async ({ page }) => {
  // Tablette
  await page.setViewportSize({ width: 820, height: 1180 });
  await page.goto(WS_URL);
  await page.waitForSelector('#app.active', { timeout: 5000 });
  await page.screenshot({ path: path.join(REPORT_DIR, '13-workspace-tablet.png'), fullPage: true });

  // Mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await page.waitForSelector('#app.active', { timeout: 5000 });

  // Hamburger visible
  await expect(page.locator('.hamb')).toBeVisible();

  // Ouvre sidebar via hamburger
  await page.click('.hamb');
  await page.waitForTimeout(300);
  await expect(page.locator('#sidebar.open')).toBeVisible();

  await page.screenshot({ path: path.join(REPORT_DIR, '13-workspace-mobile-menu.png'), fullPage: true });
});
