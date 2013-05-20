import random

from pylons.i18n import set_lang
import sqlalchemy.exc

import ckan.logic
import ckan.lib.maintain as maintain
from ckan.lib.search import SearchError
from ckan.lib.base import *
from ckan.lib.helpers import url_for

import ckan.lib.dictization.model_dictize as model_dictize
import ckan.logic as logic
from ckan.logic import get_action, NotFound
_get_or_bust = logic.get_or_bust
_check_access = logic.check_access

CACHE_PARAMETER = '__cache'
from ckanext.pat.plugin import CATEGORY_VOCAB

class HomeController(BaseController):
    repo = model.repo

    def _get_category_list(self, context):
        vocab_data = {'id': CATEGORY_VOCAB}
        try:
            vocab = get_action('vocabulary_show')(context, vocab_data)
        except NotFound:
            raise
        data_dict = {'all_fields': True, 'vocabulary_id':vocab['id']}
        tag_list = get_action('tag_list')(context, data_dict)
        return tag_list

    def __before__(self, action, **env):
        try:
            BaseController.__before__(self, action, **env)
            context = {'model': model, 'user': c.user or c.author}
            ckan.logic.check_access('site_read', context)
        except ckan.logic.NotAuthorized:
            abort(401, _('Not authorized to see this page'))
        except (sqlalchemy.exc.ProgrammingError,
                sqlalchemy.exc.OperationalError), e:
            # postgres and sqlite errors for missing tables
            msg = str(e)
            if ('relation' in msg and 'does not exist' in msg) or \
                    ('no such table' in msg):
                # table missing, major database problem
                abort(503, _('This site is currently off-line. Database '
                             'is not initialised.'))
                # TODO: send an email to the admin person (#1285)
            else:
                raise

    def index(self):
        try:
            # package search
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author}
            data_dict = {
                'q': '*:*',
                'facet.field': g.facets,
                'rows': 0,
                'start': 0,
                'fq': 'capacity:"public"'
            }
            query = ckan.logic.get_action('package_search')(
                context, data_dict)
            c.package_count = query['count']

            c.facets = query['facets']
            maintain.deprecate_context_item(
              'facets',
              'Use `c.search_facets` instead.')

            c.search_facets = query['search_facets']
            
            tag_list = self._get_category_list(context)
            results = []
            for tag in tag_list:
                tag_data_dict = {'id': tag['id'], 'package_details':False}
                try:
                    tag_details = self._tag_show(context, tag_data_dict)
                    results.append({'id':tag['id'], 'display_name':tag['display_name'], 'description':u'', 'packages':len(tag_details['packages'])})
                    #results.append(Category(tag['id'], tag['display_name'], u'', len(tag_details['packages'])))
                except NotFound:
                    #abort(404, _('Tag not found'))
                    pass
            #data_dict = {'order_by': 'packages', 'all_fields': 1}
            ## only give the terms to group dictize that are returned in the
            ## facets as full results take a lot longer
            #if 'groups' in c.search_facets:
            #    data_dict['groups'] = [ item['name'] for item in
            #        c.search_facets['groups']['items'] ]
            #c.groups = ckan.logic.get_action('group_list')(context, data_dict)
            #print "RESULTS", results
            sorted_results = sorted(results, key=lambda k: k['packages'], reverse=True)
            #print "SORTED RESULTS", sorted_results
            c.categories = sorted_results

        except SearchError, se:
            c.package_count = 0
            #c.groups = []
            c.categories = []

        if c.userobj is not None:
            msg = None
            url = url_for(controller='user', action='edit')
            is_google_id = \
                c.userobj.name.startswith(
                    'https://www.google.com/accounts/o8/id')
            if not c.userobj.email and (is_google_id and
                                        not c.userobj.fullname):
                msg = _(u'Please <a href="{link}">update your profile</a>'
                        u' and add your email address and your full name. '
                        u'{site} uses your email address'
                        u' if you need to reset your password.'.format(link=url,
                        site=g.site_title))
            elif not c.userobj.email:
                msg = _('Please <a href="%s">update your profile</a>'
                        ' and add your email address. ') % url + \
                    _('%s uses your email address'
                        ' if you need to reset your password.') \
                    % g.site_title
            elif is_google_id and not c.userobj.fullname:
                msg = _('Please <a href="%s">update your profile</a>'
                        ' and add your full name.') % (url)
            if msg:
                h.flash_notice(msg, allow_html=True)

        c.recently_changed_packages_activity_stream = \
            ckan.logic.action.get.recently_changed_packages_activity_list_html(
                context, {})

        return render('home/index.html', cache_force=True)

    def license(self):
        return render('home/license.html')

    def about(self):
        return render('home/about.html')

    def faq(self):
        return render('home/faq.html')

    def cache(self, id):
        '''Manual way to clear the caches'''
        if id == 'clear':
            wui_caches = ['stats']
            for cache_name in wui_caches:
                cache_ = cache.get_cache(cache_name, type='dbm')
                cache_.clear()
            return 'Cleared caches: %s' % ', '.join(wui_caches)

    def cors_options(self, url=None):
        # just return 200 OK and empty data
        return ''

    def _tag_show(self, context, data_dict):
        '''Return the details of a tag and all its datasets.
    
        :param id: the name or id of the tag
        :type id: string
    
        :param package_details: if False details are not returned
        :type package_details: boolean
    
        :returns: the details of the tag, including a list of all of the tag's
            datasets and their details (if needed)
        :rtype: dictionary
    
        '''
        model = context['model']
        id = _get_or_bust(data_dict, 'id')
    
        tag = model.Tag.get(id)
        context['tag'] = tag
    
        if tag is None:
            raise NotFound
    
        _check_access('tag_show',context, data_dict)
    
        tag_dict = model_dictize.tag_dictize(tag,context)
    
        if data_dict.has_key('package_details') and data_dict['package_details'] == False:
            pass
        else:
            extended_packages = []
            for package in tag_dict['packages']:
                pkg = model.Package.get(package['id'])
                extended_packages.append(model_dictize.package_dictize(pkg,context))
        
            tag_dict['packages'] = extended_packages
    
        return tag_dict
