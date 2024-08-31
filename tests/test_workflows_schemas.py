from ddeutil.observe.routes.workflows.schemas import PipelineCreate


def test_workflow_schema():
    # NOTE: This data return from ddeutil-workflow api.
    value = {
        "name": "pipe-scheduling",
        "params": {"asat-dt": {"type": "datetime"}},
        "on": [
            {"cronjob": "*/3 * * * *", "timezone": "Asia/Bangkok"},
            {"cronjob": "* * * * *", "timezone": "Asia/Bangkok"},
        ],
        "jobs": {
            "condition-job": {
                "id": "condition-job",
                "stages": [
                    {"name": "Empty stage"},
                    {
                        "name": "Call-out",
                        "echo": "Hello ${{ params.asat-dt | fmt('%Y-%m-%d') }}",
                    },
                ],
            }
        },
    }
    rs = PipelineCreate.model_validate(value)
    print(rs)
