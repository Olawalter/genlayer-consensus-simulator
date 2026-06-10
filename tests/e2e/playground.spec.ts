import { test, expect } from "@playwright/test";
test("playground loads", async ({ page }) => {
  await page.goto("/playground");
  await expect(page).toHaveTitle(/GenLayer/);
});
