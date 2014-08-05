# coding: utf8

import os
from zipfile import ZipFile

from docutils.parsers.rst import roles
from docutils.writers import Writer
from docutils.core import publish_file
from docutils.nodes import GenericNodeVisitor, Inline, TextElement

class ruby(Inline, TextElement):
    base = ''
    text = ''
    children = []

    def __init__(self, base, text):
        self.base = base
        self.text = text

def ruby_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    base, ruby_text = text.split(u'|')
    node = ruby(base, ruby_text)
    return [node], []

roles.register_local_role('ruby', ruby_role)

class Co3kNodeVisitor(GenericNodeVisitor):
    output = []
    section_level = 0
    paragraph_style = None
     
    def default_visit(self, node):
        self.output.append('[{}]'.format(type(node)))
     
    def default_departure(self, node):
        self.output.append('[/{}]'.format(type(node)))
     
    def visit_Text(self, node):
        self.output.append(node.astext())

    def depart_Text(self, node):
        pass
     
    def visit_paragraph(self, node):
        if self.paragraph_style:
            self.output.append('<text:p text:style-name="' + self.paragraph_style + '">')

    def depart_paragraph(self, node):
        if self.paragraph_style:
            self.output.append('</text:p>\n')

    def visit_ruby(self, node):
        self.output.append(
            u'<text:ruby text:style-name="ruby">'
            u'<text:ruby-base>{}</text:ruby-base>'
            u'<text:ruby-text text:style-name="ruby-text">{}</text:ruby-text>'
            u'</text:ruby>'.format(node.base, node.text)
        )

    def depart_ruby(self, node):
        pass

    def visit_author(self, node):
        self.output.append('<text:p text:style-name="document-author">')

    def depart_author(self, node):
        self.output.append('</text:p>\n')

    def visit_definition_list_item(self, node):
        self.output.append('<text:p text:style-name="paragraph">')

    def depart_definition_list_item(self, node):
        self.output.append('</text:p>\n')

    def visit_term(self, node):
        self.output.append('<text:span text:style-name="speaker">')

    def depart_term(self, node):
        self.output.append('</text:span>')

    def visit_strong(self, node):
        self.output.append('<text:span text:style-name="strong">')

    def depart_strong(self, node):
        self.output.append('</text:span>')

    def visit_definition(self, node):
        self.output.append(u'　')

    def visit_section(self, node):
        self.section_level += 1
        self.output.append('\n\n<text:p text:style-name="page-break"/>\n\n')

    def depart_section(self, node):
        self.section_level -= 1

    def visit_title(self, node):
        if self.section_level:
            self.output.append('<text:p text:style-name="section-title-level-{}">'.format(self.section_level))
        else:
            self.output.append('<text:p text:style-name="document-title">')
     
    def depart_title(self, node):
        self.output.append('</text:p><text:p text:style-name="paragraph"/>\n')
     
    def depart_definition(self, node):
        pass

    def visit_definition_list(self, node):
        pass

    def depart_definition_list(self, node):
        pass

    def visit_line_block(self, node):
        self.output.append('\n<text:p text:style-name="paragraph"/>\n')

    def depart_line_block(self, node):
        self.output.append('\n<text:p text:style-name="paragraph"/>\n')

    def visit_line(self, node):
        self.output.append('<text:p text:style-name="togaki">')

    def depart_line(self, node):
        self.output.append('</text:p>\n')


    def visit_note(self, node):
        self.paragraph_style = 'note'

    def depart_note(self, node):
        self.paragraph_style = None

    def visit_docinfo(self, node):
        pass

    def depart_docinfo(self, node):
        pass

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

 
class Co3kWriter(Writer):
    output = None
    visitor = None
     
    def translate(self):
        visitor = Co3kNodeVisitor(self.document)
        self.document.walkabout(visitor)
         
        self.output = ''.join(visitor.output).replace(u'—', u'―').replace(u' <', u'<').replace(u'> ', u'>')
 
content = publish_file(source_path='main.rst', writer=Co3kWriter(), destination_path='/dev/null')

special_files = ['mimetype', 'content.xml']

with ZipFile('main.odt', 'w') as z:
    z.write('./template/mimetype', 'mimetype')
    z.writestr('content.xml', open('./template/content.xml').read().replace('{{content}}', content))

    for path, _, filenames in os.walk('./template'):
        for filename in filenames:
            if filename in special_files:
                continue

            _path = os.path.join(path, filename)
            z.write(_path, _path.replace('./template', ''))
