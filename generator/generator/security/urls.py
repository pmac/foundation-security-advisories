# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls import url

from generator.security.utils import page
from generator.security.views import (
    AdvisoriesView,
    AdvisoryView,
    KVRedirectsView,
    OldAdvisoriesListView,
    OldAdvisoriesView,
    ProductView,
    ProductVersionView,
)


urlpatterns = (
    page('', 'security/index.html'),
    page('bug-bounty', 'security/bug-bounty.html'),
    page('client-bug-bounty', 'security/client-bug-bounty.html'),
    page('web-bug-bounty', 'security/web-bug-bounty.html'),
    page('bug-bounty/faq', 'security/bug-bounty/faq.html'),
    page('bug-bounty/faq-webapp', 'security/bug-bounty/faq-webapp.html'),
    page('bug-bounty/hall-of-fame', 'security/bug-bounty/hall-of-fame.html'),
    page('bug-bounty/web-eligible-sites', 'security/bug-bounty/web-eligible-sites.html'),
    page('bug-bounty/web-hall-of-fame', 'security/bug-bounty/web-hall-of-fame.html'),
    url(r'^advisories/$',
        AdvisoriesView.as_view(), name='security.advisories'),
    url(r'^advisories/mfsa(?P<pk>\d{4}-\d{2,3})/$',
        AdvisoryView.as_view(), name='security.advisory'),

    page('known-vulnerabilities', 'security/known-vulnerabilities.html'),
    page('known-vulnerabilities/older-vulnerabilities', 'security/older-vulnerabilities.html'),
    url(r'^known-vulnerabilities/(?P<slug>[a-z-]+)/$',
        ProductView.as_view(), name='security.product-advisories'),
    url(r'^known-vulnerabilities/(?P<product>[\w\s-]+)-(?P<version>[\d.]+)/$',
        ProductVersionView.as_view(), name='security.product-version-advisories'),
    url(r'^known-vulnerabilities/(?P<filename>.*)\.html$', KVRedirectsView.as_view()),

    url(r'^(?:announce|advisories)(?:/.*)?/mfsa(?P<pk>\d{4}-\d{2,3})\.html$',
        OldAdvisoriesView.as_view()),
    url(r'^announce/$', OldAdvisoriesListView.as_view()),
)
