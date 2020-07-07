import json

from django.shortcuts import render
from django.template.defaultfilters import date, time
from django.views.generic import TemplateView
from haystack.query import SearchQuerySet, SQ
from rest_framework.response import Response
from rest_framework.views import APIView


class SearchView(TemplateView):

    def get(self, request, *args, **kwargs):

        return render(request, 'hs_discover/index.html', {})


class SearchAPI(APIView):

    def do_clean_data(self):
        """
        Stub function for data validation to be moved elsewhere


        if self.cleaned_data.get('q'):
        The prior code corrected for an failed match of complete words, as documented
        in issue #2308. This version instead uses an advanced query syntax in which
        "word" indicates an exact match and the bare word indicates a stemmed match.
        cdata = self.cleaned_data.get('q')
        """

    def do_assign_haystack(self, NElng, SWlng, NElat, SWlat):
        """

        :return:
        """
        if NElng and SWlng:
            geo_sq = SQ(east__lte=float(NElng))
            geo_sq.add(SQ(east__gte=float(SWlng)), SQ.AND)
        else:
            geo_sq = SQ(east__gte=float(SWlng))
            geo_sq.add(SQ(east__lte=float(180)), SQ.OR)
            geo_sq.add(SQ(east__lte=float(NElng)), SQ.AND)
            geo_sq.add(SQ(east__gte=float(-180)), SQ.AND)

        if NElat and SWlat:
            # latitude might be specified without longitude
            if geo_sq is None:
                geo_sq = SQ(north__lte=float(NElat))
            else:
                geo_sq.add(SQ(north__lte=float(NElat)), SQ.AND)
            geo_sq.add(SQ(north__gte=float(SWlat)), SQ.AND)

    def get(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
                "title":
                "link":
                "availability": list value, js will parse JSON as Array
                "availabilityurl":
                "type": single value, pass a string to REST client
                "author": single value, pass a string to REST client
                "contributor": single value, pass a string to REST client
                "author_link":
                "owner": single value, pass a string to REST client
                "abstract":
                "subject":
                "created":
                "modified":
        """
        sqs = SearchQuerySet().all()

        if request.GET.get('searchtext'):
            searchtext = request.GET.get('searchtext')
            sqs = sqs.filter(content=searchtext).boost('keyword', 2.0)

        NElat = request.GET.get('nelat')
        NElng = request.GET.get('nelng')
        SWlat = request.GET.get('swlat')
        SWlng = request.GET.get('swlng')
        start_date = request.GET.get('swlng')
        end_date = request.GET.get('swlng')
        coverage_type = request.GET.get('swlng')

        sort_order = None  # sorting is handled by frontend
        sort_direction = None  # reinstate only if pagination requires backend coordination

        # self.do_clean_data()
        # self.do_assign_haystack(NElng, SWlng, NElat, SWlat)
        geo_sq = None

        if geo_sq is not None:
            sqs = sqs.filter(geo_sq)

        # allow overlapping ranges
        # cs < s < ce OR s < cs => s < ce
        # AND
        # cs < e < ce OR e > ce => cs < e
        if start_date and end_date:
            sqs = sqs.filter(SQ(end_date__gte=start_date) & SQ(start_date__lte=end_date))
        elif start_date:
            sqs = sqs.filter(SQ(end_date__gte=start_date))
        elif end_date:
            sqs = sqs.filter(SQ(start_date__lte=end_date))

        if coverage_type:
            sqs = sqs.filter(coverage_types__in=[coverage_type])

        # vocab = []  # will be populated with autocomplete terms from resource
        # vocab = [x for x in vocab if len(x) > 2]
        # vocab = list(set(vocab))
        # vocab = sorted(vocab)

        resources = []

        for result in sqs:
            print(date(result.created))
            resources.append({
                "title": result.title,
                "link": result.absolute_url,
                "availability": result.availability,
                "availabilityurl": "/static/img/{}.png".format(result.availability[0]),
                "type": result.resource_type_exact,
                "author": result.author,
                "contributor": result.creator[0],
                "author_link": result.author_url,
                "owner": result.owner[0],
                "abstract": result.abstract,
                "subject": result.subject,
                # "created": date(result.created, "M d, Y") + " at " + time(result.created),
                # "modified": date(result.modified, "M d, Y") + " at " + time(result.modified),
                "created": result.created.isoformat(),
                "modified": result.created.isoformat(),
                "shareable": True
            })

        return Response({
            'resources': json.dumps(resources),
            # 'vocab': vocab,
        })
