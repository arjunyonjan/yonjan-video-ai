const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 60000,
  fullyParallel: true,
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], headless: true },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'], headless: true },
    },
  ],
});
