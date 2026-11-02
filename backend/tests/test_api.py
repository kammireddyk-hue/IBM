import unittest
from pathlib import Path

from backend.app import create_app


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DatasetApiTests(unittest.TestCase):
    def setUp(self):
        app = create_app({"TESTING": True, "DATASET_DIR": PROJECT_ROOT})
        self.client = app.test_client()

    def test_health_reports_all_ten_datasets(self):
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["dataset_count"], 10)

    def test_frontend_is_served_from_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Institutional datasets", response.data)
        response.close()

    def test_frontend_stylesheet_is_served(self):
        response = self.client.get("/assets/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b".hero", response.data)
        response.close()

    def test_catalogue_contains_all_institutions(self):
        response = self.client.get("/api/v1/institutions")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["count"], 10)
        self.assertEqual(payload["institutions"][0]["id"], "01")
        self.assertEqual(payload["institutions"][0]["name"], "Northridge State University")

    def test_unknown_institution_returns_not_found(self):
        response = self.client.get("/api/v1/institutions/99")

        self.assertEqual(response.status_code, 404)

    def test_document_endpoint_serves_pdf(self):
        response = self.client.get("/api/v1/institutions/01/document")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        response.close()

    def test_search_returns_page_matches(self):
        response = self.client.get("/api/v1/search?q=retention&institution_id=01")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertGreater(payload["count"], 0)
        self.assertIn("page", payload["results"][0])
        self.assertIn("snippet", payload["results"][0])

    def test_search_requires_query(self):
        response = self.client.get("/api/v1/search")

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
