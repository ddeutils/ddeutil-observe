from src.ddeutil.observe.routes.audit.schemas import AuditCreate


def test_audit_schema():
    value = {
        "release": "20240902093600",
        "logs": [
            {
                "name": "wf-scheduling",
                "release": "2025-01-06 18:47:00+07:00",
                "type": "task",
                "context": {
                    "params": {"asat-dt": "2025-01-06 18:47:00+07:00"},
                    "jobs": {
                        "condition-job": {
                            "matrix": {},
                            "stages": {
                                "6708019737": {"outputs": {}},
                                "0663452000": {"outputs": {}},
                            },
                        }
                    },
                },
                "parent_run_id": "426592786720250106184702647269",
                "run_id": "426592786720250106184702647269",
                "update": "2025-01-06 18:47:02.781320",
            },
        ],
    }
    rs = AuditCreate.model_validate(value)
    assert rs.release == 20240902093600
    assert len(rs.logs) == 1
