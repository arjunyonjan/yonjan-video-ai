const { test, expect } = require('@playwright/test');
const path = require('path');

test.use({ baseURL: 'file://' });

const reportPath = 'file://' + path.resolve('/home/arjun/projects/yonjan-video-ai/spiderman-frames/report_helios.html');

test.describe('Spider-Man BND Trailer Report', () => {
  test('should load and have correct title', async ({ page }) => {
    await page.goto(reportPath);
    await expect(page).toHaveTitle(/Spider-Man BND Trailer/);
  });

  test('should display 162 frames', async ({ page }) => {
    await page.goto(reportPath);
    const frames = page.locator('img[src^="frames/frame_"]');
    await expect(frames).toHaveCount(162);
  });

  test('should have Moondream descriptions', async ({ page }) => {
    await page.goto(reportPath);
    const descriptions = page.locator('text=Moondream');
    const count = await descriptions.count();
    expect(count).toBeGreaterThanOrEqual(160);
  });

  test('should have OCR text on some frames', async ({ page }) => {
    await page.goto(reportPath);
    const ocrSections = page.locator('text=OCR Text');
    const count = await ocrSections.count();
    console.log(`Frames with OCR: ${count}`);
    expect(count).toBeGreaterThan(0);
  });

  test('should show RTX 5060 timing', async ({ page }) => {
    await page.goto(reportPath);
    const timing = page.locator('text=RTX 5060');
    await expect(timing.first()).toBeVisible();
  });

  test('YouTube iframe should exist', async ({ page }) => {
    await page.goto(reportPath);
    const ytContainer = page.locator('#yt-player');
    await expect(ytContainer).toBeVisible();
  });

  test('Hide Trailer button toggles video', async ({ page }) => {
    await page.goto(reportPath, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#trailer-video', { timeout: 5000 });
    const video = page.locator('#trailer-video');
    await expect(video).toBeVisible({ timeout: 3000 });
    const btn = page.locator('button').filter({ hasText: 'Hide Trailer' });
    await btn.click({ timeout: 3000 });
    await expect(video).toBeHidden({ timeout: 3000 });
    const showBtn = page.locator('button').filter({ hasText: 'Show Trailer' });
    await showBtn.click({ timeout: 3000 });
    await expect(video).toBeVisible({ timeout: 3000 });
  });

  test('data-seek attribute exists on frame timestamps', async ({ page }) => {
    await page.goto(reportPath, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('[data-seek]', { timeout: 5000 });
    const seekers = page.locator('[data-seek]');
    const count = await seekers.count();
    expect(count).toBeGreaterThan(100);
    const val = await seekers.first().getAttribute('data-seek');
    expect(parseInt(val)).not.toBeNaN();
  });
});
