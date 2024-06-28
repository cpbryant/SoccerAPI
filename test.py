import unittest
from unittest.mock import patch, MagicMock
import main


@patch('main.requests.get')
def test_get_groups_data(self, mock_get):
    mock_response = MagicMock()
    expected_data = {'key' : 'value'}
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get.return_value = mock_response

    groups_url = "https://euro-20242.p.rapidapi.com/groups"
    headers = {
        "x-rapidapi-key": "bba200fd56mshe960f0b2d77da71p110687jsnd7a81dfd6206",
        "x-rapidapi-host": "euro-20242.p.rapidapi.com"
    }

    data = main.get_groups_data(groups_url, headers)
    self.assertEqual(data, expected_data)



# def test_searchTeam(searchTeam):
