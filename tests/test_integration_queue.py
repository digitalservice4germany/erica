import json
import os
import requests

from tests.utils import json_default, create_unlock_code_request, is_valid_uuid, create_unlock_code_activation, \
    generate_uuid, create_unlock_code_revocation, create_tax_number_validity, create_send_est

ERICA_TESTING_URL = os.environ.get("ERICA_TESTING_URL", "http://0.0.0.0:8000")


class TestV2Ping:

    def test_if_get_from_ping_then_return_pong(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/ping")
        assert response.text == '"pong"'


class TestV2UnlockCodeRequest:

    def test_if_post_with_full_data_then_return_201(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/request",
                                 data=json.dumps(create_unlock_code_request(), default=json_default))
        assert response.status_code == 201
        response_content = response.json().split("/")
        assert response_content[0] == "request"
        assert is_valid_uuid(response_content[1])

    def test_if_post_without_full_data_then_return_422(self):
        request_payload = create_unlock_code_request()
        request_payload.clientIdentifier = None
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/request",
                                 data=json.dumps(request_payload, default=json_default))
        assert response.status_code == 422

    def test_if_get_existing_request(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/request",
                                 data=json.dumps(create_unlock_code_request(), default=json_default))
        assert response.status_code == 201
        uuid = response.json().split("/")[1]
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/request/" + uuid)
        assert response.status_code == 200
        assert "processStatus" in response.json()
        assert "result" in response.json()
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()

    def test_if_get_non_existing_request(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/request/" + str(generate_uuid()))
        assert response.status_code == 500
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()


class TestV2UnlockCodeActivation:

    def test_if_post_with_full_data_then_return_201(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/activation",
                                 data=json.dumps(create_unlock_code_activation(), default=json_default))
        assert response.status_code == 201
        response_content = response.json().split("/")
        assert response_content[0] == "request"
        assert is_valid_uuid(response_content[1])

    def test_if_post_without_full_data_then_return_422(self):
        request_payload = create_unlock_code_activation()
        request_payload.clientIdentifier = None
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/activation",
                                 data=json.dumps(request_payload, default=json_default))
        assert response.status_code == 422

    def test_if_get_existing_request(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/activation",
                                 data=json.dumps(create_unlock_code_activation(), default=json_default))
        assert response.status_code == 201
        uuid = response.json().split("/")[1]
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/activation/" + uuid)
        assert response.status_code == 200
        assert "processStatus" in response.json()
        assert "result" in response.json()
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()

    def test_if_get_non_existing_request(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/activation/" + str(generate_uuid()))
        assert response.status_code == 500
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()


class TestV2UnlockCodeRevocation:

    def test_if_post_with_full_data_then_return_201(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/revocation",
                                 data=json.dumps(create_unlock_code_revocation(), default=json_default))
        assert response.status_code == 201
        response_content = response.json().split("/")
        assert response_content[0] == "request"
        assert is_valid_uuid(response_content[1])

    def test_if_post_without_full_data_then_return_422(self):
        request_payload = create_unlock_code_revocation()
        request_payload.clientIdentifier = None
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/revocation",
                                 data=json.dumps(request_payload, default=json_default))
        assert response.status_code == 422

    def test_if_get_existing_request(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/fsc/revocation",
                                 data=json.dumps(create_unlock_code_revocation(), default=json_default))
        assert response.status_code == 201
        uuid = response.json().split("/")[1]
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/revocation/" + uuid)
        assert response.status_code == 200
        assert "processStatus" in response.json()
        assert "result" in response.json()
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()

    def test_if_get_non_existing_request(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/fsc/revocation/" + str(generate_uuid()))
        assert response.status_code == 500
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()


class TestV2TaxNumberValidity:

    def test_if_post_with_full_data_then_return_201(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/tax_number_validity",
                                 data=json.dumps(create_tax_number_validity(), default=json_default))
        assert response.status_code == 201
        response_content = response.json().split("/")
        assert response_content[0] == "request"
        assert is_valid_uuid(response_content[1])

    def test_if_post_without_full_data_then_return_422(self):
        request_payload = create_tax_number_validity()
        request_payload.clientIdentifier = None
        response = requests.post(ERICA_TESTING_URL + "/v2/tax_number_validity",
                                 data=json.dumps(request_payload, default=json_default))
        assert response.status_code == 422

    def test_if_get_existing_request(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/tax_number_validity",
                                 data=json.dumps(create_tax_number_validity(), default=json_default))
        assert response.status_code == 201
        uuid = response.json().split("/")[1]
        response = requests.get(ERICA_TESTING_URL + "/v2/tax_number_validity/" + uuid)
        assert response.status_code == 200
        assert "processStatus" in response.json()
        assert "result" in response.json()
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()

    def test_if_get_non_existing_request(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/tax_number_validity/" + str(generate_uuid()))
        assert response.status_code == 500
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()


class TestV2SendEst:

    def test_if_post_with_full_data_then_return_201(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/ests",
                                 data=json.dumps(create_send_est(), default=json_default))
        assert response.status_code == 201
        response_content = response.json().split("/")
        assert response_content[0] == "request"
        assert is_valid_uuid(response_content[1])

    def test_if_post_without_full_data_then_return_422(self):
        request_payload = create_send_est()
        request_payload.clientIdentifier = None
        response = requests.post(ERICA_TESTING_URL + "/v2/ests",
                                 data=json.dumps(request_payload, default=json_default))
        assert response.status_code == 422

    def test_if_get_existing_request(self):
        response = requests.post(ERICA_TESTING_URL + "/v2/ests",
                                 data=json.dumps(create_send_est(), default=json_default))
        assert response.status_code == 201
        uuid = response.json().split("/")[1]
        response = requests.get(ERICA_TESTING_URL + "/v2/ests/" + uuid)
        assert response.status_code == 200
        assert "processStatus" in response.json()
        assert "result" in response.json()
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()

    def test_if_get_non_existing_request(self):
        response = requests.get(ERICA_TESTING_URL + "/v2/ests/" + str(generate_uuid()))
        assert response.status_code == 500
        assert "errorCode" in response.json()
        assert "errorMessage" in response.json()
