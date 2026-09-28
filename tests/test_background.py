import background

SECRET_HEADER = 'X-Telegram-Bot-Api-Secret-Token'


def test_webhook_rejects_wrong_secret():
    client = background.app.test_client()
    response = client.post(
        background.WEBHOOK_PATH, data=b'{}', headers={SECRET_HEADER: 'wrong'}
    )
    assert response.status_code == 403
    assert background.updates.empty()


def test_webhook_enqueues_update_for_bot_process():
    client = background.app.test_client()
    body = b'{"update_id": 1}'
    response = client.post(
        background.WEBHOOK_PATH,
        data=body,
        headers={SECRET_HEADER: background.WEBHOOK_SECRET},
    )
    assert response.status_code == 200
    assert background.updates.get() == body
