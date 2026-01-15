from app.api.routes.kpi import import_kpi
from app.schemas import KPIImportRequest


def test_kpi_import(db_session):
    payload = KPIImportRequest(
        name="Test",
        csv_text="campaign,leads\nA,10",
        mapping={"campaign": "campaign", "leads": "leads"},
    )
    result = import_kpi(payload, db_session)
    assert result["rows"] == 1
