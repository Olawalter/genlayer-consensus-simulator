import { test, expect } from "@playwright/test";
test("appeals page loads", async ({ page }) => {
  await page.goto("/appeals");
});
