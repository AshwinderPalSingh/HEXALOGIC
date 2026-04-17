from api.index import app


def test_v2_api_creates_isolated_sessions_and_uses_json_state():
    app.testing = True

    with app.test_client() as first:
        first_state = first.get("/api/v2/state")
        assert first_state.status_code == 200
        first_payload = first_state.get_json()
        first_session = first_payload["session_id"]
        assert first_payload["telemetry"]["server_generated_at_ms"] > 0
        assemble_one = first.post("/api/v2/assemble", json={"code": "MOV A,#01H\nEND"})
        assert assemble_one.status_code == 200
        step_one = first.post("/api/v2/step")
        assert step_one.status_code == 200
        assert step_one.get_json()["state"]["registers"]["A"] == 0x01

    with app.test_client() as second:
        second_state = second.get("/api/v2/state")
        assert second_state.status_code == 200
        second_session = second_state.get_json()["session_id"]
        assert first_session != second_session

        assemble_two = second.post("/api/v2/assemble", json={"code": "MOV A,#02H\nEND"})
        assert assemble_two.status_code == 200
        step_two = second.post("/api/v2/step")
        assert step_two.status_code == 200
        assert step_two.get_json()["state"]["registers"]["A"] == 0x02


def test_v2_api_reports_structured_assembly_errors():
    app.testing = True

    with app.test_client() as client:
        response = client.post("/api/v2/assemble", json={"code": "MOVX @DPTR\nEND"})

        assert response.status_code == 400
        payload = response.get_json()
        assert payload["error"]["type"] == "assembly"
        assert payload["error"]["context"]["line"] == 1


def test_v2_api_validates_input_ranges():
    app.testing = True

    with app.test_client() as client:
        response = client.post("/api/v2/pins", json={"port": 9, "bit": 0, "level": 1})

        assert response.status_code == 400
        payload = response.get_json()
        assert payload["error"]["type"] == "validation"
        assert payload["error"]["context"]["field"] == "port"


def test_v2_api_supports_architecture_switch_endian_debug_and_metrics():
    app.testing = True

    with app.test_client() as client:
        response = client.post("/api/v2/architecture", json={"architecture": "arm"})
        assert response.status_code == 200
        assert response.get_json()["architecture"] == "arm"

        response = client.post("/api/v2/endian", json={"endian": "big"})
        assert response.status_code == 200
        assert response.get_json()["endian"] == "big"

        response = client.post("/api/v2/debug", json={"enabled": True})
        assert response.status_code == 200
        assert response.get_json()["debug_mode"] is True

        assemble = client.post(
            "/api/v2/assemble",
            json={
                "code": "\n".join(
                    [
                        "ORG 0000H",
                        "MOV R0, #4",
                        "MOV R1, #12",
                        "ADD R2, R0, R1",
                        "END",
                    ]
                )
            },
        )
        assert assemble.status_code == 200
        step = client.post("/api/v2/step")
        assert step.status_code == 200
        assert step.get_json()["state"]["architecture"] == "arm"

        metrics = client.get("/api/v2/metrics")
        assert metrics.status_code == 200
        payload = metrics.get_json()["metrics"]
        assert payload["active_sessions"] >= 1
        assert "api_requests" in payload


def test_v2_api_rejects_oversized_source_payloads():
    app.testing = True
    previous_limit = app.config["HEXLOGIC_MAX_SOURCE_CHARS"]
    app.config["HEXLOGIC_MAX_SOURCE_CHARS"] = 8

    try:
        with app.test_client() as client:
            response = client.post("/api/v2/assemble", json={"code": "MOV A,#01H\nEND"})

            assert response.status_code == 400
            payload = response.get_json()
            assert payload["error"]["type"] == "validation"
    finally:
        app.config["HEXLOGIC_MAX_SOURCE_CHARS"] = previous_limit


def test_v2_api_step_back_and_session_export_import():
    app.testing = True

    with app.test_client() as client:
        assemble = client.post("/api/v2/assemble", json={"code": "MOV A,#01H\nINC A\nEND"})
        assert assemble.status_code == 200

        step_one = client.post("/api/v2/step")
        assert step_one.status_code == 200
        step_two = client.post("/api/v2/step")
        assert step_two.status_code == 200
        assert step_two.get_json()["state"]["registers"]["A"] == 0x02

        rewind = client.post("/api/v2/step-back")
        assert rewind.status_code == 200
        assert rewind.get_json()["state"]["registers"]["A"] == 0x01

        exported = client.get("/api/v2/export")
        assert exported.status_code == 200
        session_payload = exported.get_json()["export"]

    with app.test_client() as client:
        imported = client.post("/api/v2/import", json={"session": session_payload})
        assert imported.status_code == 200
        payload = imported.get_json()
        assert payload["registers"]["A"] == 0x01
        assert payload["has_program"] is True


def test_v2_api_step_response_includes_telemetry():
    app.testing = True

    with app.test_client() as client:
        assemble = client.post("/api/v2/assemble", json={"code": "MOV A,#01H\nEND"})
        assert assemble.status_code == 200

        step = client.post("/api/v2/step")
        assert step.status_code == 200
        payload = step.get_json()
        assert payload["telemetry"]["server_generated_at_ms"] > 0
