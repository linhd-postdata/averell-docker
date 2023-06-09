# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'averell'
year = '2019-2020'
author = 'LINHD POSTDATA Project'
copyright = '{0}, {1}'.format(year, author)
version = release = '1.2.2'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/linhd-postdata/averell/issues/%s', '#'),
    'pr': ('https://github.com/linhd-postdata/averell/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

#if not on_rtd:  # only set the theme if we're building docs locally
html_theme = 'alabaster'
html_theme_options = {
    'badge_branch': "develop",
    'github_user': 'linhd-postdata',
    'github_repo': 'averell',
    'github_banner': True,
    'body_text_align': 'justify',
    'fixed_sidebar': True,
}

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
