def test_get_sales_dashboard(client):
    response = client.get("/analytics/dashboard")
    assert response.status_code == 200

def test_get_sales_forecasts(client):
    response = client.get("/analytics/forecasts")
    assert response.status_code == 200

def test_get_sales_performance(client):
    response = client.get("/analytics/performance")
    assert response.status_code == 200

