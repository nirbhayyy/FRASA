from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings 
urlpatterns = [
    path("",home,name="home"),
    path("login/",login_view,name='login'),
    path("register/",register_views,name='register'),
    path("logout/",logout_view,name='logout'),
    path("pred_rev/",predict_reviews,name='predict_review'),
    path("cheack/",check_review,name='check_review'),
    path("pred_senti/",predict_sentimets,name='check_sentimet'),
    path("get_rev/",get_reviews,name='history'),
    path("how_it_work/",how_it_work,name='how_it_work'),
    path("dashboard/",dashboard,name='dashboard'),
    path('bulk/',       bulk_check_page,       name='bulk_check'),
    path('bulk_pred/',  bulk_predict_reviews,  name='bulk_predict'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)