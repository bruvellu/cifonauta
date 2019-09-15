from django.urls import path
from . import views
from . import models

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = [
        path('', views.home_page, name='home'),

        # Menu
        path('search/', views.search_page, name='search_url'),
        path('organization/', views.org_page, name='org_url'),
        path('tags/', views.tags_page, name='tags_url'),
        path('taxa/', views.taxa_page, name='taxa_url'),
        path('places/', views.places_page, name='places_url'),
        path('authors/', views.authors_page, name='persons_url'),
        path('literature/', views.refs_page, name='refs_url'),
        path('tours/', views.tours_page, name='tours_url'),
        path('press/', views.press_page, name='press_url'),

        path('tag/<slug:slug>/', views.meta_page, extra(models.Tag, 'tag'), name='tag_url'),
        path('author/<slug:slug>/', views.meta_page, extra(models.Person, 'person'), name='person_url'),
        path('taxon/<slug:slug>/', views.meta_page, extra(models.Taxon, 'taxon'), name='taxon_url'),
        path('size/(<slug:slug>/', views.meta_page, extra(models.Size, 'size'), name='size_url'),
        path('place/<slug:slug>/', views.meta_page, extra(models.Sublocation, 'sublocation'), name='sublocation_url'),
        path('city/<slug:slug>/', views.meta_page, extra(models.City, 'city'), name='city_url'),
        path('state/<slug:slug>/', views.meta_page, extra(models.State, 'state'), name='state_url'),
        path('country/<slug:slug>/', views.meta_page, extra(models.Country, 'country'), name='country_url'),
        path('reference/<slug:slug>/', views.meta_page, extra(models.Reference, 'reference'), name='reference_url'),

        path('tour/<slug:slug>/', views.tour_page, name='tour_url'),
        path('media/<int:media_id>/', views.media_page, name='media_url'),

        # TODO: Prepare to redirect old URLs.
        #url(r'^photo/(\d+)/$', media_page, name='image_url'),
        #url(r'^video/(\d+)/$', media_page, name='video_url'),

        ]
