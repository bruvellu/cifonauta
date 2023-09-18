from django.urls import path
from . import views
from .views import CuradoriaMediaList, MediaDetail, MyMedias, RevisionMedia

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = [
        path('', views.home_page, name='home'),

        # Módulo administrativo
        path('administrative-module/', views.dashboard, name='dashboard'),
        path('administrative-module/add/load-media', views.upload_media_step1, name='upload_media_step1'),
        path('administrative-module/add/fulfill-metadata', views.upload_media_step2, name='upload_media_step2'),
        path('administrative-module/edit-metadata/<int:media_id>', views.edit_metadata, name='edit_metadata'),
        path('administrative-module/details/<int:pk>/', MediaDetail.as_view(), name='media_detail'),
        path('administrative-module/update/<int:pk>', views.update_my_medias, name='update_media'),
        path('administrative-module/curadory-medias/', CuradoriaMediaList.as_view(), name='curadory_medias'),
        path('administrative-module/my-medias/', MyMedias.as_view(), name='my_medias'),
        path('administrative-module/revision', RevisionMedia.as_view(), name='media_revision'),

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

        # Media pages
        path('tour/<slug:slug>/', views.tour_page, name='tour_url'),
        path('media/<int:media_id>/', views.media_page, name='media_url'),
        path('photo/<int:old_id>/', views.old_media, {'datatype':'image'}),
        path('video/<int:old_id>/', views.old_media, {'datatype': 'video'}),

        # Meta pages
        path('tag/<slug:slug>/', views.search_page, extra('Tag', 'tag'),
            name='tag_url'),
        path('author/<slug:slug>/', views.search_page, extra('Person',
            'author'), name='person_url'),
        path('taxon/<slug:slug>/', views.search_page, extra('Taxon', 'taxon'),
            name='taxon_url'),
        path('place/<slug:slug>/', views.search_page, extra('Location',
            'location'), name='location_url'),
        path('city/<slug:slug>/', views.search_page, extra('City', 'city'),
            name='city_url'),
        path('state/<slug:slug>/', views.search_page, extra('State', 'state'),
            name='state_url'),
        path('country/<slug:slug>/', views.search_page, extra('Country',
            'country'), name='country_url'),
        path('reference/<slug:slug>/', views.search_page, extra('Reference',
            'reference'), name='reference_url'),
        ]
