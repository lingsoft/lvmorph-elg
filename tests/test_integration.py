import unittest
import json
import requests


API_URL = 'http://localhost:8000/process/'


def call_api(endpoint, text):
    url = API_URL + endpoint
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"type": "text", "content": text})
    return requests.post(url, headers=headers, data=payload).json()

class TestEndpoint(unittest.TestCase):

    def setUp(self):
        self.endpoint = "wrong"
        self.text = "roku"

    def test_invalid_endpoint(self):
        response = call_api(self.endpoint, self.text)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.service.not.found')

class TestAnalysisIntegration(unittest.TestCase):

    def setUp(self):
        self.endpoint = "word_analysis"
        self.text = "roku"

    def test_analysis_response_type(self):
        response = call_api(self.endpoint, self.text)
        self.assertEqual(response["response"]["type"], "texts")

    def test_analysis_response_content(self):
        response = call_api(self.endpoint, self.text)
        for (reading, tag) in zip(response["response"]["texts"], 
                          ["ncmsa1", "ncmpg1", "ncfsa4", "ncfpg4", "vmnip_11san"]):
            self.assertEqual(reading["content"], tag)

    def test_analysis_with_empty_request(self):
        response = call_api(self.endpoint, "")
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.input.empty")

    def test_analysis_with_too_large_request(self):
        text = self.text + " "
        large_text = text * 3001
        response = call_api(self.endpoint, large_text)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                         "elg.request.too.large")

    def test_analysis_with_long_token(self):
        long_token = "A" * 10000
        response = call_api(self.endpoint, long_token)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                "lingsoft.token.too.long")

    def test_analysis_with_special_characters(self):
        spec_text = "\N{grinning face}\u4e01\u0009" + self.text + "\u0008"
        response = call_api(self.endpoint, spec_text)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                         "lingsoft.character.invalid")
    
    def test_analysis_with_unknown_word(self):
        unknown_word = "dhfdgdfhsh"
        response = call_api(self.endpoint, unknown_word)
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.not.found.word")

    def test_analysis_with_multiple_words(self):
        multiple_words = "roku rakt"
        response = call_api(self.endpoint, multiple_words)
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.input.not.single")

class TestWordformsIntegration(unittest.TestCase):

    def setUp(self):
        self.endpoint = "wordforms"
        self.text = "rakt"

    def test_wordforms_response_type(self):
        response = call_api(self.endpoint, self.text)
        self.assertEqual(response["response"]["type"], "texts")

    def test_wordforms_response_content(self):
        response = call_api(self.endpoint, self.text)
        self.assertEqual(len(response["response"]["texts"]), 1030)
        self.assertEqual(response["response"]["texts"][0]["content"], "vmnn0_1000n")

    def test_wordforms_with_empty_request(self):
        response = call_api(self.endpoint, "")
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.input.empty")

    def test_wordforms_with_too_large_request(self):
        text = self.text + " "
        large_text = text * 3001
        response = call_api(self.endpoint, large_text)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                         "elg.request.too.large")

    def test_wordforms_with_long_token(self):
        long_token = "A" * 10000
        response = call_api(self.endpoint, long_token)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                "lingsoft.token.too.long")

    def test_wordforms_with_special_characters(self):
        spec_text = "\N{grinning face}\u4e01\u0009" + self.text + "\u0008"
        response = call_api(self.endpoint, spec_text)
        self.assertEqual(response["failure"]["errors"][0]["code"],
                         "lingsoft.character.invalid")
    
    def test_wordforms_with_unknown_word(self):
        unknown_word = "dhfdgdfhsh"
        response = call_api(self.endpoint, unknown_word)
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.not.found.word")

    def test_wordforms_with_multiple_words(self):
        multiple_words = "rakt roku"
        response = call_api(self.endpoint, multiple_words)
        self.assertEqual(response["response"]["warnings"][0]["code"],
                         "lingsoft.input.not.single")

if __name__ == '__main__':
    unittest.main()
