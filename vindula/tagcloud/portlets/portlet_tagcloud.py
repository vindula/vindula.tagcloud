# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from vindula.tagcloud.vocabularies import SubjectsVocabularyFactory
from vindula.tagcloud import MessageFactory as _

class ITagCloudPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)
    
    
    title_portlet = schema.TextLine(title=unicode("Título", 'utf-8'),
                                  description=unicode("Título que aparecerá no cabeçalho do portlet.", 'utf-8'),
                                  required=True)
    
    count = schema.Int(title = _(u"Número máximo de tags mostradas."),
                       description = _(u"Se maior que 0 este número limitará as tags mostradas."),
                       required = True,
                       min = 0,
                       default = 0)
    
    pathSearch = schema.TextLine(title=unicode("Busca de conteudo", 'utf-8'),
                                  description=unicode("digite o link da pagina de busca para mais conteudo relacionado.", 'utf-8'),
                                  required=True)
    
    restrictSubjects = schema.List(required = False,
                                    title = _(u"Restringir por palavras-chaves"),
                                    description = _(u"Restringe as palavras-chaves buscadas. Deixar este campo vazio incluirá todas as palavras-chaves."),
                                    value_type = schema.Choice(vocabulary = 
                                        'vindula.tagcloud.subjects'))

    filterSubjects = schema.List(
        required = False,
        title = _(u"Filtrar por palavras-chaves"),
        description = _(u"Filtra palavras-chaves buscadas. Somente itens categorizados com ao menos todas as palavras-chaves selecionadas serão buscados." \
                         "As palavras-chaves selecionadas serão omitidas da nuvem de tags. Deixar o campo vazio desabilita o filtro."),
        value_type = schema.Choice(vocabulary =
            'vindula.tagcloud.subjects'),
        )

    restrictTypes = schema.List(
        required = False,
        title = _(u"Restringir por tipo"),
        description = _(u"Restringe por tipo de conteúdo. Deixar este campo vazio incluirá todos os tipos de conteúdo permitidos."),
        value_type = schema.Choice(vocabulary =
            'plone.app.vocabularies.ReallyUserFriendlyTypes'),
        )

    wfStates = schema.List(
            required = True,
            title = _(u"Restringir por estado do workflow"),
            description = _(u"Que estados serão incluídos na busca."),
            value_type = schema.Choice(vocabulary =
                                       'plone.app.vocabularies.WorkflowStates'))
    
    
    


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ITagCloudPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, title_portlet=u'',pathSearch=u'', count=0, restrictSubjects=[], filterSubjects=[],
        restrictTypes=[], wfStates=[]):
        self.title_portlet = title_portlet
        self.count = count
        self.pathSearch = pathSearch
        self.restrictSubjects = restrictSubjects
        self.filterSubjects = filterSubjects
        self.restrictTypes = restrictTypes
        self.wfStates = wfStates
        

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Tag Cloud"
    
    def get_title(self):
        return self.data.title_portlet
    

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('portlet_tagcloud.pt')

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ITagCloudPortlet)

    def create(self, data):
        return Assignment(**data)

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ITagCloudPortlet)
    def __call__(self):
        subjectFields = ['restrictSubjects', 'filterSubjects']
        for fieldname in subjectFields:
            field = self.form_fields.get(fieldname).field
            existing = field.get(self.context)
            subject_vocab = SubjectsVocabularyFactory(self.context)
            all_subjects = set([t.title for t in subject_vocab])
            valid = all_subjects.intersection(existing)
            if not valid == set(existing):
                field.set(self.context, list(valid))
        return super(EditForm, self).__call__()
