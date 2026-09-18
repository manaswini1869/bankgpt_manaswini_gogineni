from pathlib import Path

from app.artifact.schema import ActionType, CapabilityArtifact


class PlaywrightCodeGenerator:
    def generate(self, artifact: CapabilityArtifact) -> str:
        lines = [
            "import pytest",
            "from playwright.async_api import Page, expect",
            "",
            f"@pytest.mark.asyncio\nasync def test_{artifact.id}(page: Page):",
            f'    await page.goto({artifact.entrypoint!r})',
            "",
        ]
        input_defaults = {name: param.default for name, param in artifact.inputs.items()}
        for name in artifact.inputs:
            if input_defaults.get(name) is None:
                input_defaults[name] = name.upper()
        for step in artifact.steps:
            if step.action == ActionType.NAVIGATE:
                lines.append(f"    await page.goto({self._render_value(step.value, input_defaults)!r})")
            elif step.action == ActionType.FILL:
                value = self._render_value(step.value, input_defaults)
                if value and value in {name.upper() for name in input_defaults}:
                    value_expr = value
                else:
                    value_expr = repr(value)
                lines.append(f"    await {self._locator(step.target.locator)}.fill({value_expr})")
            elif step.action == ActionType.CLICK:
                lines.append(f"    await {self._locator(step.target.locator)}.click()")
            elif step.action == ActionType.EXTRACT:
                var = step.output or "extracted_value"
                lines.append(f"    {var} = await {self._locator(step.target.locator)}.inner_text()")
            elif step.action == ActionType.WAIT:
                lines.append(f"    await page.wait_for_timeout({step.value})")
        if artifact.checkpoint.strategy == "text":
            lines.append(f"    await expect(page.get_by_text({artifact.checkpoint.expected!r})).to_be_visible()")
        elif artifact.checkpoint.strategy == "url":
            lines.append(f"    await expect(page).to_have_url(lambda url: {artifact.checkpoint.expected!r} in url)")
        return "\n".join(lines) + "\n"

    def _locator(self, locator) -> str:
        if locator.strategy == "test_id":
            return f"page.get_by_test_id({locator.value!r})"
        if locator.strategy == "role":
            if locator.name is not None:
                return f"page.get_by_role({locator.value!r}, name={locator.name!r})"
            return f"page.get_by_role({locator.value!r})"
        if locator.strategy == "label":
            return f"page.get_by_label({locator.value!r})"
        if locator.strategy == "text":
            return f"page.get_by_text({locator.value!r})"
        return f"page.locator({locator.value!r})"

    @staticmethod
    def _render_value(value: str | None, inputs: dict) -> str | None:
        if value is None:
            return None
        rendered = value
        for name, replacement in inputs.items():
            rendered = rendered.replace("{{" + name + "}}", name.upper())
        return rendered

    def write(self, artifact: CapabilityArtifact, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{artifact.id}_test.py"
        path.write_text(self.generate(artifact))
        return path
