import os

from playwright.async_api import async_playwright

from app.surface.base import Surface, SurfaceState


class PlaywrightSurface(Surface):
    def __init__(self):
        self._pw = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self, entrypoint: str, headless: bool = True):
        self._pw = await async_playwright().start()
        executable_path = os.getenv("PLAYWRIGHT_EXECUTABLE_PATH")
        launch_kwargs = {"headless": headless}
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        self.browser = await self._pw.chromium.launch(**launch_kwargs)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.goto(entrypoint, wait_until="domcontentloaded")

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()

    async def observe(self) -> SurfaceState:
        title = await self.page.title()
        body = await self.page.locator("body").inner_text()
        return SurfaceState(url=self.page.url, title=title, text=body[:20_000])

    async def navigate(self, url: str):
        await self.page.goto(url, wait_until="domcontentloaded")

    def resolve(self, locator):
        strategy = locator.strategy
        if strategy == "test_id":
            return self.page.get_by_test_id(locator.value)
        if strategy == "role":
            return self.page.get_by_role(locator.value, name=locator.name)
        if strategy == "label":
            return self.page.get_by_label(locator.value)
        if strategy == "text":
            return self.page.get_by_text(locator.value)
        if strategy == "css":
            return self.page.locator(locator.value)
        raise ValueError(f"Unsupported locator strategy: {strategy}")

    async def click(self, locator, timeout_ms: int):
        await self.resolve(locator).click(timeout=timeout_ms)

    async def fill(self, locator, value: str, timeout_ms: int):
        await self.resolve(locator).fill(value, timeout=timeout_ms)

    async def extract(self, locator, timeout_ms: int) -> str:
        return (await self.resolve(locator).inner_text(timeout=timeout_ms)).strip()

    async def wait(self, ms: int):
        await self.page.wait_for_timeout(ms)

    async def screenshot(self, path: str):
        await self.page.screenshot(path=path, full_page=True)
