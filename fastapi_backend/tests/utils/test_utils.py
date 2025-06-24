from fastapi.routing import APIRoute
from app.utils import simple_generate_unique_route_id


def test_simple_generate_unique_route_id(mocker):
    mock_route = mocker.Mock(spec=APIRoute)

    mock_route.tags = ["auth"]
    mock_route.name = "authenticate_user"

    unique_id = simple_generate_unique_route_id(mock_route)

    assert unique_id == "auth-authenticate_user"
