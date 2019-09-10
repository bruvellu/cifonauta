from django.urls import path
from . import views
from . import models

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = [
        path('', views.main_page, name='home'),

        # Menu
        path('search/', views.search_page, name='search_url'),
        path('organization/', views.org_page, name='org_url'),
        path('tags/', views.tags_page, name='tags_url'),
        path('taxa/', views.taxa_page, name='taxa_url'),
        path('places/', views.places_page, name='places_url'),
        path('authors/', views.authors_page, name='authors_url'),
        path('literature/', views.refs_page, name='refs_url'),
        path('tours/', views.tours_page, name='tours_url'),
        path('press/', views.press_page, name='press_url'),

        path('tag/<slug:slug>/', views.meta_page, extra(models.Tag, 'tag'), name='tag_url'),
        path('author/<slug:slug>/', views.meta_page, extra(models.Author, 'author'), name='author_url'),
        path('source/<slug:slug>/', views.meta_page, extra(models.Source, 'source'), name='source_url'),
        path('taxon/<slug:slug>/', views.meta_page, extra(models.Taxon, 'taxon'), name='taxon_url'),
        path('size/(<slug:slug>/', views.meta_page, extra(models.Size, 'size'), name='size_url'),
        path('place/<slug:slug>/', views.meta_page, extra(models.Sublocation, 'sublocation'), name='sublocation_url'),
        path('city/<slug:slug>/', views.meta_page, extra(models.City, 'city'), name='city_url'),
        path('state/<slug:slug>/', views.meta_page, extra(models.State, 'state'), name='state_url'),
        path('country/<slug:slug>/', views.meta_page, extra(models.Country, 'country'), name='country_url'),
        path('reference/<slug:slug>/', views.meta_page, extra(models.Reference, 'reference'), name='reference_url'),
        path('tour/<slug:slug>/', views.tour_page, name='tour_url'),
        path('photo/<int:image_id>/', views.photo_page, name='image_url'),
        path('video/<int:video_id>/', views.video_page, name='video_url'),
        path('embed/<int:video_id>/', views.embed_page, name='embed_url'),
        ]
