from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import District, Region, StaticPage, Setting


class CommonEndpointsTests(APITestCase):
    def setUp(self):
        self.static_page = StaticPage.objects.create(
            slug="about-us",
            title="About Us",
            content="This is about us page content",
            is_active=True
        )

        self.inactive_page = StaticPage.objects.create(
            slug="inactive-page",
            title="Inactive Page",
            content="This is inactive page content",
            is_active=False
        )

        self.region1 = Region.objects.create(name="Tashkent")
        self.region2 = Region.objects.create(name="Samarkand")
        self.district1 = District.objects.create(name="Chilanzar", region=self.region1)
        self.district2 = District.objects.create(name="Yashnabad", region=self.region1)
        self.district3 = District.objects.create(name="Siab", region=self.region2)
        self.setting = Setting.objects.create(
            phone="+998901234567",
            support_email="support@test.com",
            working_hours="Monday-Sunday 9:00-21:00",
            maintenance_mode=False
        )

    def test_static_pages_list(self):
        url = reverse("static-page-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        page_titles = [page["title"] for page in response.data["data"]["results"]]
        self.assertIn(self.static_page.title, page_titles)
        self.assertNotIn(self.inactive_page.title, page_titles)

    def test_static_pages_list_empty(self):
        StaticPage.objects.all().delete()

        url = reverse("static-page-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_static_page_detail(self):
        url = reverse("static-page-detail", kwargs={"slug": self.static_page.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], self.static_page.title)
        self.assertEqual(response.data["data"]["content"], self.static_page.content)

    def test_static_page_detail_not_found(self):
        url = reverse("static-page-detail", kwargs={"slug": "non-existent-page"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)

    def test_static_page_detail_inactive(self):
        url = reverse("static-page-detail", kwargs={"slug": self.inactive_page.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_regions_with_districts(self):
        url = reverse("regions-with-districts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])


        region_names = [region["name"] for region in response.data["data"]["results"]]
        self.assertIn(self.region1.name, region_names)
        self.assertIn(self.region2.name, region_names)


        tashkent_region = next(r for r in response.data["data"]["results"] if r["name"] == "Tashkent")
        district_names = [d["name"] for d in tashkent_region["districts"]]
        self.assertIn("Chilanzar", district_names)
        self.assertIn("Yashnabad", district_names)

    def test_regions_with_districts_empty(self):

        Region.objects.all().delete()

        url = reverse("regions-with-districts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_regions_with_districts_no_districts(self):

        District.objects.all().delete()

        url = reverse("regions-with-districts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        for region in response.data["data"]["results"]:
            self.assertEqual(len(region["districts"]), 0)

    def test_common_settings(self):
        url = reverse("setting-detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])


        data = response.data["data"]
        if isinstance(data, dict) and "results" in data:
            setting_data = data["results"][0]
        else:
            setting_data = data

        self.assertEqual(setting_data["phone"], self.setting.phone)
        self.assertEqual(setting_data["support_email"], self.setting.support_email)
        self.assertEqual(setting_data["working_hours"], self.setting.working_hours)
        self.assertEqual(setting_data["maintenance_mode"], self.setting.maintenance_mode)

    def test_common_settings_auto_create(self):
        Setting.objects.all().delete()

        url = reverse("setting-detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        data = response.data["data"]
        if isinstance(data, dict) and "results" in data:
            setting_data = data["results"][0]
        else:
            setting_data = data

        self.assertEqual(setting_data["phone"], "+998770367366")  # Default qiymat
        self.assertEqual(setting_data["support_email"], "support@77.uz")  # Default qiymat

    def test_api_response_format(self):
        url = reverse("static-page-list")
        response = self.client.get(url)

        self.assertIn("success", response.data)
        self.assertIn("data", response.data)
        self.assertTrue(isinstance(response.data["success"], bool))

        if response.data["data"]:
            self.assertIn("results", response.data["data"])
            self.assertTrue(isinstance(response.data["data"]["results"], list))

    def test_api_error_response_format(self):
        url = reverse("static-page-detail", kwargs={"slug": "non-existent"})
        response = self.client.get(url)

        self.assertIn("success", response.data)
        self.assertIn("errors", response.data)
        self.assertFalse(response.data["success"])

    def test_regions_ordering(self):
        Region.objects.create(name="Andijan")
        Region.objects.create(name="Bukhara")

        url = reverse("regions-with-districts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        region_names = [region["name"] for region in response.data["data"]["results"]]
        self.assertEqual(region_names, sorted(region_names))

    def test_districts_in_region(self):
        url = reverse("regions-with-districts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tashkent_region = next(r for r in response.data["data"]["results"] if r["name"] == "Tashkent")
        self.assertEqual(len(tashkent_region["districts"]), 2)

        samarkand_region = next(r for r in response.data["data"]["results"] if r["name"] == "Samarkand")
        self.assertEqual(len(samarkand_region["districts"]), 1)

    def test_pagination_support(self):
        for i in range(15):
            StaticPage.objects.create(
                slug=f"page-{i}",
                title=f"Page {i}",
                content=f"Content {i}",
                is_active=True
            )

        url = reverse("static-page-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if "count" in response.data["data"]:
            self.assertIn("count", response.data["data"])
            self.assertIn("next", response.data["data"])
            self.assertIn("previous", response.data["data"])

    def test_content_type_headers(self):
        url = reverse("static-page-list")
        response = self.client.get(url)

        self.assertEqual(response["content-type"], "application/json")

    def test_performance_prefetch_related(self):
        for i in range(10):
            region = Region.objects.create(name=f"Region {i}")
            for j in range(5):
                District.objects.create(name=f"District {i}-{j}", region=region)

        url = reverse("regions-with-districts")

        with self.assertNumQueries(2):  # 1 - regions, 1 - districts
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)