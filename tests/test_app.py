from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def ensure_participant(activity_name: str, email: str):
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)


def remove_participant_if_exists(activity_name: str, email: str):
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def test_get_activities_returns_initial_activities():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert "participants" in data[activity_name]
    assert isinstance(data[activity_name]["participants"], list)
    assert "michael@mergington.edu" in data[activity_name]["participants"]


def test_signup_for_activity_succeeds_and_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "test_signup@example.com"
    remove_participant_if_exists(activity_name, email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    try:
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    finally:
        remove_participant_if_exists(activity_name, email)


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate_signup@example.com"
    ensure_participant(activity_name, email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

    remove_participant_if_exists(activity_name, email)


def test_remove_participant_succeeds_when_participant_exists():
    # Arrange
    activity_name = "Programming Class"
    email = "test_remove@example.com"
    ensure_participant(activity_name, email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "missing_remove@example.com"
    remove_participant_if_exists(activity_name, email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_for_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "invalid_activity@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_for_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "invalid_activity@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
