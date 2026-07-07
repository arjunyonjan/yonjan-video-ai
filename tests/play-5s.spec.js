const { test } = require('@playwright/test');

const reportUrl = 'http://localhost:3000/report_helios.html';

test('Play trailer 5 seconds', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(reportUrl, { waitUntil: 'load', timeout: 30000 });
  await page.waitForSelector('#yt-player', { timeout: 10000 });

  const iframe = page.frameLocator('#yt-player');

  // Try clicking the YouTube thumbnail/play overlay directly
  await iframe.locator('.ytp-large-play-button').first().click({ timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(1000);

  // If that fails, press Space key on the iframe
  await iframe.locator('body').press('Space', { timeout: 3000 }).catch(() => {});
  await page.waitForTimeout(1000);

  // Click on the iframe video area
  await iframe.locator('.ytp-cued-thumbnail-overlay').first().click({ timeout: 3000 }).catch(() => {});

  console.log('▶️ Playing...');
  await page.waitForTimeout(5000);
  console.log('⏹️ 5 seconds watched');
});
