import pytest
from playwright.async_api import Page, expect

MEMBER_ID = "12345"

@pytest.mark.asyncio
async def test_lookup_member_balance(page: Page):
    await page.goto('http://127.0.0.1:8000')

    await page.get_by_label('Member ID').fill(MEMBER_ID)
    await page.get_by_role('button', name='Search').click()
    savings_balance = await page.get_by_label('Savings Balance').inner_text()
    await expect(page.get_by_text('Member Details')).to_be_visible()
