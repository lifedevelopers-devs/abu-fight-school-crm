from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='login'),
    path('index/', views.home, name='index'),
    path('davomat/', views.davomat, name='davomat'),
    path('davomat-guruh/', views.davomat_guruh, name='davomat-guruh'),
    path('azolar/', views.azolar, name='azolar'),
    path('tolov/', views.tolov, name='tolov'),
    path('yangiliklar/', views.yangiliklar, name='yangiliklar'),
    path('dokon/', views.dokon, name='dokon'),
    path('profil/', views.profil, name='profil'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('maxfiylik/', views.maxfiylik, name='maxfiylik'),
    path('ota-ona-login/', views.ota_ona, name='ota-ona-login'),
    path('ota-ona/', views.ota_ona_portal, name='ota-ona'),
    path('ota-ona-1-guruh/', views.ota_ona_1, name='ota-ona-1'),
    path('ota-ona-2-guruh/', views.ota_ona_2, name='ota-ona-2'),
    path('ota-ona-3-guruh/', views.ota_ona_3, name='ota-ona-3'),
    path('ota-ona-4-guruh/', views.ota_ona_4, name='ota-ona-4'),
    path('ota-ona-5-guruh/', views.ota_ona_5, name='ota-ona-5'),
    path('ota-ona-6-guruh/', views.ota_ona_6, name='ota-ona-6'),
    path('dev-console/', views.dev_console, name='dev-console'),
    path('sw.js', views.service_worker, name='sw'),
    path('manifest.json', views.manifest, name='manifest'),
    path('offline/', views.offline, name='offline'),
]
