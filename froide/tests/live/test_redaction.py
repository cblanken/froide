from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

import pytest
from playwright.async_api import Page

from froide.foirequest.tests import factories

from .utils import do_login

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio(loop_scope="session")
async def test_set_status(
    page: Page,
    world,
    live_server,
    foi_request_factory,
    foi_message_factory,
):
    factories.rebuild_index()
    user = User.objects.get(username="dummy")
    req = factories.FoiRequestFactory(
        user=user, created_at=timezone.now(), status="resolved"
    )
    mes = factories.FoiMessageFactory(request=req)
    att = factories.FoiAttachmentFactory(belongs_to=mes)

    await do_login(page, live_server)
    req.refresh_from_db()

    path = reverse(
        "foirequest-redact_attachment",
        kwargs={"slug": req.slug, "attachment_id": att.id},
    )
    await page.goto(live_server.url + path)

    await page.locator("#pdf-viewer").scroll_into_view_if_needed()

    await page.wait_for_timeout(500)

    await page.locator(".redactContainer").hover()
    await page.mouse.move(200, 200)
    await page.mouse.down()
    await page.wait_for_timeout(500)
    await page.mouse.move(400, 400)
    await page.mouse.up()

    await page.pause()
