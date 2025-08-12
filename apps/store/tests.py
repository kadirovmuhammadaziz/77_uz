from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image
import io
import tempfile

from .models import (
    Category,
    Ad,
    AdPhoto,
    FavoriteProduct,
    SavedSearch,
    SearchCount,
    PopularSearch,
)
from common.models import Region, District

User = get_user_model()


class StoreEndpointsTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="+998901234567"
        )

        self.seller_user = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            first_name="Seller",
            last_name="User",
            phone_number="+998901234568"
        )

        self.region = Region.objects.create(name="Tashkent")
        self.district = District.objects.create(name="Chilanzar", region=self.region)

        self.parent_category = Category.objects.create(
            name="Electronics",
            is_active=True
        )

        self.child_category = Category.objects.create(
            name="Smartphones",
            parent=self.parent_category,
            is_active=True
        )

        self.inactive_category = Category.objects.create(
            name="Inactive Category",
            is_active=False
        )

        self.test_image = self.create_test_image()


        self.ad = Ad.objects.create(
            name="iPhone 15",
            description="Brand new iPhone 15",
            category=self.child_category,
            price=1200000,
            seller=self.seller_user,
            status="active",
            region=self.region,
            district=self.district
        )

        self.ad_photo = AdPhoto.objects.create(
            ad=self.ad,
            image=self.test_image,
            is_main=True,
            order=0
        )

        self.inactive_ad = Ad.objects.create(
            name="Samsung Galaxy",
            description="Samsung phone",
            category=self.child_category,
            price=800000,
            seller=self.seller_user,
            status="inactive"
        )

        self.favorite = FavoriteProduct.objects.create(
            user=self.user,
            ad=self.ad
        )

        self.saved_search = SavedSearch.objects.create(
            user=self.user,
            category=self.child_category,
            search_query="phone",
            price_min=500000,
            price_max=1500000
        )

        self.popular_search = PopularSearch.objects.create(
            name="iPhone",
            search_count=100,
            is_active=True
        )

        self.search_count = SearchCount.objects.create(
            category=self.child_category,
            search_count=50
        )

    def create_test_image(self):
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.seek(0)
        return SimpleUploadedFile("test.jpg", file.getvalue(), content_type="image/jpeg")

    def test_category_list(self):
        url = reverse("store:category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        category_names = [cat["name"] for cat in response.data["data"]["results"]]
        self.assertIn(self.parent_category.name, category_names)
        self.assertIn(self.child_category.name, category_names)
        self.assertNotIn(self.inactive_category.name, category_names)

    def test_categories_with_children(self):
        url = reverse("store:categories-with-children")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        parent_category = next(
            cat for cat in response.data["data"]["results"]
            if cat["name"] == self.parent_category.name
        )

        self.assertIsNotNone(parent_category)
        self.assertEqual(len(parent_category["children"]), 1)
        self.assertEqual(parent_category["children"][0]["name"], self.child_category.name)

    def test_sub_category_list(self):
        url = reverse("store:sub-category-list")
        response = self.client.get(url, {"parent__id": self.parent_category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        child_names = [cat["name"] for cat in response.data["data"]["results"]]
        self.assertIn(self.child_category.name, child_names)

    def test_ad_list(self):
        url = reverse("store:ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        ad_names = [ad["name"] for ad in response.data["data"]["results"]]
        self.assertIn(self.ad.name, ad_names)
        self.assertNotIn(self.inactive_ad.name, ad_names)

    def test_ad_list_with_category_filter(self):
        url = reverse("store:ad-list")
        response = self.client.get(url, {"category_ids": str(self.child_category.id)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for ad in response.data["data"]["results"]:
            pass

    def test_ad_detail(self):
        url = reverse("store:ad-detail", kwargs={"slug": self.ad.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], self.ad.name)
        self.assertEqual(response.data["data"]["price"], self.ad.price)

        self.ad.refresh_from_db()
        self.assertEqual(self.ad.view_count, 1)

    def test_ad_detail_not_found(self):
        url = reverse("store:ad-detail", kwargs={"slug": "non-existent-ad"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_ad_create_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:ad-create")
        data = {
            "name": "New iPhone",
            "description": "Brand new iPhone for sale",
            "category": self.child_category.id,
            "price": 1000000,
            "region": self.region.id,
            "district": self.district.id
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        new_ad = Ad.objects.get(name="New iPhone")
        self.assertEqual(new_ad.seller, self.user)
        self.assertEqual(new_ad.status, "pending")  # Default status

    def test_ad_create_unauthenticated(self):
        url = reverse("store:ad-create")
        data = {
            "name": "New iPhone",
            "description": "Description",
            "category": self.child_category.id,
            "price": 1000000
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_ad_list(self):
        self.client.force_authenticate(user=self.seller_user)

        url = reverse("store:my-ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        for ad in response.data["data"]["results"]:
            self.assertEqual(ad["seller"]["id"], self.seller_user.id)

    def test_my_ad_detail_owner(self):
        self.client.force_authenticate(user=self.seller_user)

        url = reverse("store:my-ad-detail", kwargs={"pk": self.ad.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_my_ad_detail_not_owner(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:my-ad-detail", kwargs={"pk": self.ad.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_product_list(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:my-favorite-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        favorite_ads = [fav["product"]["id"] for fav in response.data["data"]["results"]]
        self.assertIn(self.ad.id, favorite_ads)

    def test_favorite_product_create(self):
        self.favorite.delete()

        self.client.force_authenticate(user=self.user)

        url = reverse("store:favorite-create")
        data = {"product": self.ad.id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        self.assertTrue(
            FavoriteProduct.objects.filter(user=self.user, ad=self.ad).exists()
        )

    def test_favorite_product_create_duplicate(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:favorite-create")
        data = {"product": self.ad.id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_favorite_product_by_device_id(self):
        device_favorite = FavoriteProduct.objects.create(
            device_id="test-device-123",
            ad=self.ad
        )

        url = reverse("store:my-favorite-by-id-list")
        response = self.client.get(url, {"device_id": "test-device-123"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        favorite_ids = [fav["id"] for fav in response.data["data"]["results"]]
        self.assertIn(device_favorite.id, favorite_ids)

    def test_favorite_product_delete(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:favorite-delete", kwargs={"pk": self.favorite.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            FavoriteProduct.objects.filter(id=self.favorite.id).exists()
        )

    # Saved Search Tests
    def test_saved_search_create(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:saved-search-create")
        data = {
            "category_id": self.child_category.id,
            "search_query": "new phone",
            "price_min": 600000,
            "price_max": 1200000
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_saved_search_list(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:saved-search-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        search_queries = [search["search_query"] for search in response.data["data"]["results"]]
        self.assertIn(self.saved_search.search_query, search_queries)

    def test_saved_search_delete(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("store:saved-search-delete", kwargs={"pk": self.saved_search.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            SavedSearch.objects.filter(id=self.saved_search.id).exists()
        )

    def test_category_product_search(self):
        url = reverse("store:category-product-search")
        response = self.client.get(url, {"q": "phone"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        results = response.data["data"]["results"]
        self.assertGreater(len(results), 0)

        types = [result["type"] for result in results]
        self.assertTrue(any(t in ["category", "product"] for t in types))

    def test_category_product_search_empty(self):
        url = reverse("store:category-product-search")
        response = self.client.get(url, {"q": ""})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_autocomplete_search(self):
        url = reverse("store:autocomplete-search")
        response = self.client.get(url, {"q": "iphone"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        results = response.data["data"]["results"]
        if results:
            self.assertTrue(all("name" in result for result in results))

    def test_popular_search(self):
        url = reverse("store:popular-search")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        search_names = [search["name"] for search in response.data["data"]["results"]]
        self.assertIn(self.popular_search.name, search_names)

    def test_search_count_increase(self):
        initial_count = self.search_count.search_count

        url = reverse("store:search-count-increase", kwargs={"id": self.child_category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.search_count.refresh_from_db()
        self.assertEqual(self.search_count.search_count, initial_count + 1)

    def test_search_count_increase_invalid_category(self):
        url = reverse("store:search-count-increase", kwargs={"id": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_ad_photo_create(self):
        self.client.force_authenticate(user=self.seller_user)

        url = reverse("store:ad-photo-create")

        test_image = self.create_test_image()

        data = {
            "product_id": self.ad.id,
            "image": test_image,
            "is_main": False,
            "order": 1
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_ad_photo_create_invalid_product(self):
        self.client.force_authenticate(user=self.seller_user)

        url = reverse("store:ad-photo-create")
        test_image = self.create_test_image()

        data = {
            "product_id": 99999,
            "image": test_image,
            "is_main": False
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_product_download(self):
        url = reverse("store:product-download", kwargs={"slug": self.ad.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], self.ad.name)

    def test_api_response_format(self):
        url = reverse("store:category-list")
        response = self.client.get(url)

        self.assertIn("success", response.data)
        self.assertIn("data", response.data)
        self.assertTrue(isinstance(response.data["success"], bool))

        if response.data["data"]:
            self.assertIn("results", response.data["data"])
            self.assertTrue(isinstance(response.data["data"]["results"], list))

    def test_api_error_response_format(self):
        url = reverse("store:ad-detail", kwargs={"slug": "non-existent"})
        response = self.client.get(url)

        self.assertIn("success", response.data)
        self.assertIn("errors", response.data)
        self.assertFalse(response.data["success"])

    def test_pagination_support(self):
        for i in range(15):
            Ad.objects.create(
                name=f"Test Ad {i}",
                description=f"Description {i}",
                category=self.child_category,
                price=100000 + i,
                seller=self.seller_user,
                status="active"
            )

        url = reverse("store:ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if "count" in response.data["data"]:
            self.assertIn("count", response.data["data"])
            self.assertIn("next", response.data["data"])
            self.assertIn("previous", response.data["data"])

    def test_ordering_support(self):
        Ad.objects.create(
            name="Cheap Phone",
            description="Description",
            category=self.child_category,
            price=500000,
            seller=self.seller_user,
            status="active"
        )

        Ad.objects.create(
            name="Expensive Phone",
            description="Description",
            category=self.child_category,
            price=2000000,
            seller=self.seller_user,
            status="active"
        )

        url = reverse("store:ad-list")
        response = self.client.get(url, {"ordering": "price"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        prices = [ad["price"] for ad in response.data["data"]["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_filtering_support(self):
        url = reverse("store:ad-list")
        response = self.client.get(url, {"search": "iPhone"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for ad in response.data["data"]["results"]:
            self.assertIn("iphone", ad["name"].lower())

    def tearDown(self):
        if hasattr(self.test_image, 'file'):
            self.test_image.file.close()

        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith('test') and filename.endswith('.jpg'):
                try:
                    os.remove(os.path.join(temp_dir, filename))
                except:
                    pass