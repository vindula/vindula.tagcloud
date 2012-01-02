# coding: utf-8
from Products.CMFPlone.utils import getToolByName
from plone.app.layout.navigation.root import getNavigationRoot
from Products.PythonScripts.standard import url_quote
from zope.i18n import translate
from vindula.tagcloud import MessageFactory as _
from Products.Five import BrowserView

class TagCloud(BrowserView):

    def calcTagSize(self, number, total, min, max):
        return int( (float(number)*float(max-min))/float(total) + min )

    def subjects(self, minsize=100, maxsize=300):
        pc = getToolByName(self.context, 'portal_catalog')
        #results = pc(self.context.buildQuery())
        results = pc()
        #total = len(results)
        total = 0
        d = {}
        for result in results:
            if result.Subject:
                subjects = result.Subject
                total = total + 1
                for subject in subjects:
                    d[subject] = d.get(subject,0) + 1
        l = [ (x,self.calcTagSize(d[x],total, min=minsize, max=maxsize),'search?Subject%3Alist=' + x ) for x in d.keys() ]
        return l
    
    
   

    def getTags(self, portlet):
        portlet_data = portlet
        portal_url = getToolByName(self.context, 'portal_url')()
        tagOccs = self.getTagOccurrences(portlet)
        # If count has been set sort by occurences and keep the "count" first
        
#        if portlet_data.count:
#            sortedOccs = sorted(tagOccs.items(),
#                                key=itemgetter(1),
#                                reverse=True)[:portlet_data.count]
#            tagOccs = dict(sortedOccs)

#        thresholds = self.getThresholds(tagOccs.values())
#        tags = list(tagOccs.keys())
#        tags.sort()
#        res = []
#        for tag in tags:
#            d = {}
#            size = self.getTagSize(tagOccs[tag], thresholds)
#            if size == 0:
#                continue
#            d["text"] = tag
#            d["class"] = "cloud" + str(size)
#            href= portal_url + \
#                "/search?Subject%3Alist="+url_quote(tag)
#            #Add type restrictions to search link
#            href = href+ "".join(["&portal_type%3Alist="+url_quote(ptype)
#                for ptype in portlet_data.restrictTypes])
#            #Add workflow restrictions to search link
#            href = href+ "".join(["&review_state%3Alist="+url_quote(wstate)
#                for wstate in portlet_data.wfStates])
#            #Add path to search link
#            href = href+"&path=%s"%getNavigationRoot(self.context)
#            d["href"]=href
#            d["count"] = translate(
#                _(u'${count} items', mapping={'count': tagOccs[tag]}),
#                context=self.request)
#            res.append(d)
#        return res

        total = 0
        minsize=100
        maxsize=300
        d = {}
        for result in tagOccs.get('result',[]):
            if result.Subject:
                subjects = result.Subject
                total = total + 1
                for subject in subjects:
                    d[subject] = d.get(subject,0) + 1
        l = [ (x,self.calcTagSize(d[x],total, min=minsize, max=maxsize),'search?Subject%3Alist=' + x ) for x in d.keys() ]
        return l

    

    def getSearchSubjects(self, portlet):
        portlet_data = portlet
        catalog = getToolByName(self.context, 'portal_catalog')
        if portlet_data.restrictSubjects:
            result = portlet_data.restrictSubjects
        else:
            result = list(catalog.uniqueValuesFor('Subject'))
        for filtertag in portlet_data.filterSubjects:
            if filtertag in result:
                result.remove(filtertag)
        return result

    def getSearchTypes(self, portlet):
        portlet_data = portlet
        putils = getToolByName(self.context, 'plone_utils')
        if portlet_data.restrictTypes:
            return portlet_data.restrictTypes
        else:
            return putils.getUserFriendlyTypes()

    def getTagOccurrences(self, portlet):
        portlet_data = portlet
        types = self.getSearchTypes(portlet)
        tags = self.getSearchSubjects(portlet)
        catalog = getToolByName(self.context, 'portal_catalog')
        filterTags = portlet_data.filterSubjects
        tagOccs = {}
        query = {}
        L = []
        query['portal_type'] = types
        query['path'] = getNavigationRoot(self.context)
        if portlet_data.wfStates:
            query['review_state'] = portlet_data.wfStates
        for tag in tags:
            result = []
            if filterTags:
                query['Subject'] = {'query': filterTags+[tag],
                                    'operator': 'and'}
            else:
                query['Subject'] = tag
            result = catalog.searchResults(**query)
            if result:
                tagOccs[tag] = len(result)
                for i in result:
                    L.append(i)
                
        tagOccs['result'] = L
        return tagOccs

    def getTagSize(self, tagWeight, thresholds):
        size = 0
        if tagWeight:
            for t in thresholds:
                size += 1
                if tagWeight <= t:
                    break
        return size

    def getThresholds(self, sizes):
        """This algorithm was taken from Anders Pearson's blog:
         http://thraxil.com/users/anders/posts/2005/12/13/scaling-tag-clouds/
        """
        if not sizes:
            return [1 for i in range(0, 5)]
        minimum = min(sizes)
        maximum = max(sizes)
        return [pow(maximum - minimum + 1, float(i) / float(5))
            for i in range(0, 5)]

    