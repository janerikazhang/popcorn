# Create your views here.

# Django
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse ####

def index(request):
    context = RequestContext(request)
    if request.method == 'GET':
        """show popcorn_app index view"""
        return render_to_response('popcorn_app/index_with_menu.html', context)

    elif request.method == 'POST':
        return query(request)


# From PuppyIR
from puppy.model import Query, Response

# From WeSe - get our service manager so we can search for results
from popcorn_app.service import service

def query(request):
    """show results for query"""
    user_query = request.POST['search']
    #results = service.search_services['web_search'].search(Query(user_query)).entries
    context = RequestContext(request)
    #results_dict = {'query': user_query, 'results': results}
    #return render_to_response('popcorn_app/results.html') #, results_dict, context
    return render_to_response('popcorn_app/query_results.html', {'query': user_query, 'results': 'result'}, context)

def query2(request):
    """show popcorn_app query view"""
    context = RequestContext(request)
    return render_to_response('popcorn_app/query_results.html', context)

def query3(request, query):
   """show popcorn_app query view"""
   context = RequestContext(request)
   return HttpResponse("You searched for %s." % query)






def film(request):
   """show popcorn_app film view"""
   context = RequestContext(request)
   return render_to_response('popcorn_app/view_film.html', context)

def reviews(request):
   """show popcorn_app reviews view"""
   context = RequestContext(request)
   return render_to_response('popcorn_app/view_reviews.html', context)


