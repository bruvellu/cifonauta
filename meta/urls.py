from django.urls import path
from . import views

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = [
        path('', views.home_page, name='home'),

        # Módulo administrativo
        path('dashboard/', views.dashboard, name='dashboard'),
        path('dashboard/upload/step-1/', views.upload_media_step1, name='upload_media_step1'),
        path('dashboard/upload/step-2/', views.upload_media_step2, name='upload_media_step2'),
        path('dashboard/editing/', views.editing_media_list, name='editing_media_list'),
        path('dashboard/editing/<int:media_id>/', views.editing_media_details, name='editing_media_details'),
        path('dashboard/revision/', views.revision_media_list, name='revision_media_list'),
        path('dashboard/revision/<int:media_id>/', views.revision_media_details, name='revision_media_details'),
        path('dashboard/revision/modified/<int:pk>/', views.revision_modified_media, name='revision_modified_media'),
        path('dashboard/manage-users/', views.manage_users, name='manage_users'),
        path('dashboard/tours/', views.tour_list, name='tour_list'),
        path('dashboard/tours/add/', views.tour_add, name='tour_add'),
        path('dashboard/tours/<int:pk>/', views.tour_details, name='tour_details'),
        path('dashboard/curations/', views.my_curations_media_list, name='my_curations_media_list'),
        path('dashboard/curations/<int:media_id>/', views.my_curations_media_details, name='my_curations_media_details'),
        path('dashboard/medias/', views.my_media_list, name='my_media_list'),
        path('dashboard/medias/<int:pk>/', views.my_media_details, name='my_media_details'),

        path('synchronize-fields', views.synchronize_fields, name='synchronize_fields'),
        path('get-tour-medias', views.get_tour_medias, name='get_tour_medias'),

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
