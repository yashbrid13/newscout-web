from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(HashTag)
admin.site.register(TrendingHashTags)
admin.site.register(Writer)
admin.site.register(Domain)
admin.site.register(Category)
admin.site.register(CategoryAssociation)
admin.site.register(Article)
admin.site.register(ArticleMedia)
admin.site.register(ArticleInteraction)
admin.site.register(SubMenu)
admin.site.register(Menu)
admin.site.register(Devices)
admin.site.register(SocialAccount)
admin.site.register(ScoutFrontier)
admin.site.register(ScoutedItem)
admin.site.register(TrendingArticle)
admin.site.register(DailyDigest)
admin.site.register(Comment)
admin.site.register(Subscription)
admin.site.register(Notification)

