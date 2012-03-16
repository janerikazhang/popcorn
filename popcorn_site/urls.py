from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'popcorn_site.views.home', name='home'),
    # url(r'^popcorn_site/', include('popcorn_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # Other URLs
        (r'^popcorn_app/$', 'popcorn_app.views.index'),
     # Previous URL's - these are not shown for clarity reasons
        (r'^popcorn_app/query/$', 'popcorn_app.views.query'),
)
