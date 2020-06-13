# Copyright (c) 2016, Isotoma Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Isotoma Limited nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ISOTOMA LIMITED BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import json
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape
from django.utils.html import format_html
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from wagtail.admin.rich_text.converters.editor_html import WhitelistRule
from wagtail.admin.templatetags.wagtailadmin_tags import hook_output
from wagtail.core import hooks
from wagtail.core.whitelist import attribute_rule, allow_without_attributes


def to_js_primitive(string):
    return mark_safe(json.dumps(escape(string)))


@hooks.register('register_rich_text_features')
def apply_whitelist(features):
    # table
    cell_attributes = attribute_rule({'rowspan': True, 'colspan': True, 'width': True, 'height': True, 'style': True})
    features.register_converter_rule('editorhtml', 'table', [
        WhitelistRule('table', attribute_rule({'style': True, 'border': True})),
        WhitelistRule('thead', allow_without_attributes),
        WhitelistRule('tbody', allow_without_attributes),
        WhitelistRule('tfoot', allow_without_attributes),
        WhitelistRule('tr', allow_without_attributes),
        WhitelistRule('th', cell_attributes),
        WhitelistRule('td', cell_attributes),
    ])
    features.default_features.append('table')

    # text
    features.register_converter_rule('editorhtml', 'span', [
        WhitelistRule('span', attribute_rule({'style': True, 'class': True})),
    ])
    features.default_features.append('span')

    features.register_converter_rule('editorhtml', 'blockquote', [
        WhitelistRule('blockquote', attribute_rule({'style': True, 'class': True})),
    ])
    features.default_features.append('blockquote')


@hooks.register('insert_editor_css')
def insert_editor_css():
    css_files = [
        'wagtailtinymce/css/icons.css',
        'wagtailtinymce/js/vendor/tinymce/skins/lightgray/skin.min.css',
        'wagtailtinymce/js/vendor/tinymce/skins/lightgray/content.min.css',
    ]
    css_includes = format_html_join(
        '\n',
        '<link rel="stylesheet" href="{0}">',
        ((static(filename),) for filename in css_files),
    )
    return css_includes + hook_output('insert_tinymce_css')


def _format_js_includes(js_files):
    return format_html_join(
        '\n',
        '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files)
    )


@hooks.register('insert_editor_js')
def insert_editor_js():
    preload = format_html(
        '<script>'
        '(function() {{'
        '    "use strict";'
        '    window.tinymce = window.tinymce || {{}};'
        '    window.tinymce.base = window.tinymce.baseURL = {};'
        '    window.tinymce.suffix = "";'
        '}}());'
        '</script>',
        to_js_primitive(static('wagtailtinymce/js/vendor/tinymce/tinymce.min.js').rsplit('/', 1)[0]),
    )
    js_includes = _format_js_includes([
        'wagtailtinymce/js/vendor/tinymce/jquery.tinymce.min.js',
        'wagtailtinymce/js/vendor/tinymce/tinymce.min.js',
        'wagtailtinymce/js/tinymce-editor.js'
    ])
    return preload + js_includes + hook_output('insert_tinymce_js')


@hooks.register('insert_tinymce_js')
def images_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtailimage", {}, {});
            window.chooserUrls.imageChooserSelectFormat = {};
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtailimage.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
        to_js_primitive(reverse('wagtailimages:chooser_select_format', args=['00000000']))
    )
    js_includes = _format_js_includes([
        'wagtailimages/js/image-chooser-modal.js',
        'wagtailimages/js/image-chooser.js'
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def embeds_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtailembeds", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtailembeds.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )
    js_includes = _format_js_includes([
        'wagtailembeds/js/embed-chooser-modal.js',
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def links_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtaillink", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtaillink.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )
    js_includes = _format_js_includes([
        'wagtailadmin/js/page-chooser.js',
        'wagtailadmin/js/page-chooser-modal.js',
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def docs_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtaildoclink", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtaildoclink.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )
    js_includes = _format_js_includes([
        'wagtaildocs/js/document-chooser.js',
        'wagtaildocs/js/document-chooser-modal.js',
    ])
    return preload + js_includes
