from abc import ABC, abstractmethod
from typing import Any


class SurfaceState(dict):
    pass


class Surface(ABC):
    @abstractmethod
    async def start(self, entrypoint: str, headless: bool = True): ...

    @abstractmethod
    async def close(self): ...

    @abstractmethod
    async def observe(self) -> SurfaceState: ...

    @abstractmethod
    async def navigate(self, url: str): ...

    @abstractmethod
    async def click(self, locator, timeout_ms: int): ...

    @abstractmethod
    async def fill(self, locator, value: str, timeout_ms: int): ...

    @abstractmethod
    async def extract(self, locator, timeout_ms: int) -> str: ...

    @abstractmethod
    async def wait(self, ms: int): ...

    @abstractmethod
    async def screenshot(self, path: str): ...
