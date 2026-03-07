from notifications_service.worker import template_for


def test_template_for_known_events() -> None:
    assert template_for("order.paid") == "order_paid"
    assert template_for("order.payment_failed") == "order_payment_failed"
    assert template_for("order.created") == "order_created"


def test_template_for_unknown_event() -> None:
    assert template_for("something.else") == "unknown_event"
