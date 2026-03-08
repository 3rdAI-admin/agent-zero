import run_ui


def test_health_is_live_even_when_not_ready():
    run_ui.startup_state.reset()
    run_ui.startup_state.mark_running(
        "chat_restore", required=True, detail="Loading saved chats."
    )

    client = run_ui.webapp.test_client()

    health_response = client.get("/health")
    ready_response = client.get("/ready")

    assert health_response.status_code == 200
    assert health_response.data == b"ok"
    assert ready_response.status_code == 503
    assert ready_response.get_json()["ready"] is False


def test_ready_reports_success_when_required_phases_are_ready():
    run_ui.startup_state.reset()
    run_ui.startup_state.mark_ready("migration", detail="Done.")
    run_ui.startup_state.mark_ready("chat_restore", detail="Done.")
    run_ui.startup_state.mark_ready("mcp_init", detail="Done.")
    run_ui.startup_state.mark_ready("preload", detail="Done.")

    client = run_ui.webapp.test_client()
    ready_response = client.get("/ready")

    body = ready_response.get_json()
    assert ready_response.status_code == 200
    assert body["ready"] is True
    assert body["phases"]["migration"]["status"] == "ready"
    assert body["phases"]["chat_restore"]["status"] == "ready"
    assert body["phases"]["mcp_init"]["status"] == "ready"
