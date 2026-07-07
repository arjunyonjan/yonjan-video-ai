const { test, expect } = require('@playwright/test');
const path = require('path');

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
});
