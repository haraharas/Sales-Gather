from django.urls import path
from .views import SaleFilterView, SaleDetailView,  SaleUpdateView, SaleDeleteView, SaleMonthView, SaleImport, SaleYearView, SaleCreateView, SaleHelp
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
admin.site.site_title = '売上集計システム'
admin.site.site_header = '売上集計システム'
admin.site.index_title = 'メニュー'
urlpatterns = [
    # 一覧画面
    path('', SaleFilterView.as_view(), name='index'),
    # 詳細画面
    path('detail/<int:pk>/', SaleDetailView.as_view(), name='detail'),
    # 登録画面
    path('create/', SaleCreateView.as_view(), name='create'),
    # 更新画面
    path('update/<int:pk>/', SaleUpdateView.as_view(), name='update'),
    # 削除画面
    path('delete/<int:pk>/', SaleDeleteView.as_view(), name='delete'),
    # 月集計
    path('month/', views.SaleMonthView, name='month'),
    # 年集計
    path('year/', views.SaleYearView, name='year'),
    # CSVインポート
    path('import/', views.SaleImport.as_view(), name='import'),
    # CSVエクスポート
    path('export/', views.sale_export, name='export'),
    # ヘルプ
    path('help/', views.SaleHelp, name='help'),
]
