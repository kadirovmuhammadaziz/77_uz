from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("category/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories-with-childs/",
        views.CategoryWithChildrenView.as_view(),
        name="categories-with-children",
    ),
    path(
        "sub-category/", views.SubCategoryListView.as_view(), name="sub-category-list"
    ),
    path("ads/", views.AdCreateView.as_view(), name="ad-create"),
    path("ads/<slug:slug>/", views.AdDetailView.as_view(), name="ad-detail"),
    path("list/ads/", views.AdListView.as_view(), name="ad-list"),
    path("my-ads/", views.MyAdListView.as_view(), name="my-ad-list"),
    path("my-ads/<int:pk>/", views.MyAdDetailView.as_view(), name="my-ad-detail"),
    path(
        "product-download/<slug:slug>/",
        views.ProductDownloadView.as_view(),
        name="product-download",
    ),
    path(
        "product-image-create/",
        views.AdPhotoCreateView.as_view(),
        name="ad-photo-create",
    ),
    path(
        "my-favourite-product/",
        views.FavoriteProductListView.as_view(),
        name="my-favorite-list",
    ),
    path(
        "my-favourite-product-by-id/",
        views.FavoriteProductByIdListView.as_view(),
        name="my-favorite-by-id-list",
    ),
    path(
        "favourite-product-create/",
        views.FavoriteProductCreateView.as_view(),
        name="favorite-create",
    ),
    path(
        "favourite-product-create-by-id/",
        views.FavoriteProductCreateByIdView.as_view(),
        name="favorite-create-by-id",
    ),
    path(
        "favourite-product/<int:pk>/delete/",
        views.FavoriteProductDeleteView.as_view(),
        name="favorite-delete",
    ),
    path(
        "favourite-product-by-id/<int:id>/delete/",
        views.FavoriteProductDeleteByIdView.as_view(),
        name="favorite-delete-by-id",
    ),
    path(
        "my-search/", views.SavedSearchCreateView.as_view(), name="saved-search-create"
    ),
    path(
        "my-search/list/", views.SavedSearchListView.as_view(), name="saved-search-list"
    ),
    path(
        "my-search/<int:pk>/delete/",
        views.SavedSearchDeleteView.as_view(),
        name="saved-search-delete",
    ),
    path(
        "search/category-product/",
        views.CategoryProductSearchView.as_view(),
        name="category-product-search",
    ),
    path(
        "search/complete/",
        views.AutoCompleteSearchView.as_view(),
        name="autocomplete-search",
    ),
    path("search/populars/", views.PopularSearchView.as_view(), name="popular-search"),
    path(
        "search/count-increase/<int:id>/",
        views.search_count_increase,
        name="search-count-increase",
    ),
]
