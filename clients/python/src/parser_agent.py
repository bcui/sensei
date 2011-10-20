import sys, json
import random, os, subprocess
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from datetime import datetime
import urllib, urllib2
import logging
import re
from sensei_client import BQLRequest, SenseiClient, SenseiClientError, SenseiRequest, DEFAULT_REQUEST_MAX_PER_GROUP
from pyparsing import ParseException

logger = logging.getLogger("parser_agent")

PARSER_AGENT_PORT = 8888

#
# Main server resource
#
class Root(resource.Resource):

  def render_GET(self, request):
    """
    get response method for the root resource
    localhost:/8888
    """
    return 'Welcome to the REST API'

  def getChild(self, name, request):
    """
    We overrite the get child function so that we can handle invalid
    requests
    """
    if name == '':
      return self
    else:
      if name in VIEWS.keys():
        return resource.Resource.getChild(self, name, request)
      else:
        return PageNotFoundError()

class PageNotFoundError(resource.Resource):

  def render_GET(self, request):
    return 'Page Not Found!'


class ParseBQL(resource.Resource):

  def render_GET(self, request):
    """Start a BQL parser server."""
    try:
      info = request.args["info"][0]
      info = json.loads(info.encode('utf-8'))

      req = BQLRequest(info["bql"])
      result = json.dumps(construct_ucp_json(req, info), sort_keys=True)

      return json.dumps({
          "ok": True,
          "result": result
          })
    except ParseException as err:
      print err
      return json.dumps(
        {
          "ok": False,
          "error": "Parsing error at location %s: %s" % (err.loc, err.msg)
          })

    except Exception as err:
      print err
      return "Error"

  def render_POST(self, request):
    return self.render_GET(request)

# To make the process of adding new views less static
VIEWS = {
  "parse": ParseBQL()
}

def construct_ucp_json(request, info,
                       max_per_group=DEFAULT_REQUEST_MAX_PER_GROUP):
  """Construct BQL query template for UCP."""

  variables = re.findall(r"\$[a-zA-Z0-9]+", info["bql"])
  variables = list(set(variables))
  info["auxParams"] = {"array": [ {"name": var[1:]} for var in variables ]}

  output_selections = []
  for field, selection in request.get_selections().iteritems():
    select_dict = {}
    select_dict["name"] = selection.field
    select_dict["valueOperation"] = selection.operation.upper()
    if selection.values:
      select_dict["selection"] = {"array": [val for val in selection.values]}
    if selection.excludes:
      select_dict["exclude"] = {"array": [val for val in selection.excludes]}
    output_selections.append(select_dict)

  output_facets = []
  for field, facet in request.get_facets().iteritems():
    facet_dict = {}
    facet_dict["name"] = field
    facet_dict["minHitCount"] = facet.minHits
    facet_dict["maxHitCount"] = facet.maxCounts
    facet_dict["orderBy"] = facet.orderBy == "hits" and "HITS" or "VALUE"
    output_facets.append(facet_dict)

  output_sorts = []
  for sort in request.get_sorts():
    sort_dict = {}
    sort_dict["name"] = sort.field
    sort_dict["sortOrder"] = sort.dir.upper()
    output_sorts.append(sort_dict)

  output = {
    "name": info["name"],
    "description": info["description"],
    "feedQuery" : {
      "urn": info["urn"],
      "auxParams": info["auxParams"]
      },
    "bql": info["bql"],
    "filters": {
      "com.linkedin.ucp.query.models.QueryFilters": {
        "keywords": {
          "array": [request.get_query()]
          },
        "facetSelections": {
          "array": output_selections
          }
        }
      },
    "facets": {
      "array": output_facets
      },
    "order": {
      "array": output_sorts
      },
    "groupBy": {
      "com.linkedin.ucp.query.models.QueryFacetGroupBySpec": {
        "name": request.get_groupby(),
        "maxHitsPerGroup": request.get_max_per_group() or max_per_group
        }
      }
    }
  return output

def main(argv):
  from optparse import OptionParser
  usage = "usage: %prog [options]"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--interactive", action="store_true", dest="interactive",
                    default=False, help="Run UCP parser in interactive mode")
  parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    default=False, help="Turn on verbose mode")
  (options, args) = parser.parse_args()

  if not options.interactive:
    return

  if options.verbose:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)d - %(message)s")
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  import readline
  readline.parse_and_bind("tab: complete")
  while True:
    try:
      stmt = raw_input('> ')
      if stmt == "exit":
        break
      req = BQLRequest(stmt)
      info = {
        "name": "nus_member",
        "description": "Test BQL query template generator",
        "urn": "urn:feed:nus:member:exp:a:$memberId",
        "bql": stmt
        }
      print json.dumps(construct_ucp_json(req, info), sort_keys=True, indent=4)
    except EOFError:
      break
    except ParseException as err:
      print " " * (err.loc + 2) + "^\n" + err.msg
    except SenseiClientError as err:
      print err
  sys.exit()

if __name__ == '__main__':
  main(sys.argv)

  root = Root()
  for viewName, className in VIEWS.items():
    root.putChild(viewName, className)
  log.startLogging(sys.stdout)
  log.msg('Starting parser agent: %s' %str(datetime.now()))
  server = server.Site(root)
  reactor.listenTCP(PARSER_AGENT_PORT, server)
  reactor.run()

"""
To test, just issue the following command.  It's important to remember
that semicolons in the statement, if you use them, have to be encoded as
"%3B":

$ curl -X POST 'http://localhost:8888/parse' -d 'info={"name":"nus_member", "description":"Test Description", "urn":"urn:feed:nus:member:exp:a:$memberId", "bql":"select * from cars where memberId in (\"$memberId\") group by color top 5 %3B"} '

{"ok": true, "result": "{\"bql\": \"select * from cars where memberId in (\\\"$memberId\\\") group by color top 5 ;\", \"description\": \"Test Description\", \"facets\": {\"array\": []}, \"feedQuery\": {\"auxParams\": {\"array\": [{\"name\": \"memberId\"}]}, \"urn\": \"urn:feed:nus:member:exp:a:$memberId\"}, \"filters\": {\"com.linkedin.ucp.query.models.QueryFilters\": {\"facetSelections\": {\"array\": [{\"name\": \"memberId\", \"selection\": {\"array\": [\"$memberId\"]}, \"valueOperation\": \"OR\"}]}, \"keywords\": {\"array\": [\"\"]}}}, \"groupBy\": {\"com.linkedin.ucp.query.models.QueryFacetGroupBySpec\": {\"maxHitsPerGroup\": 5, \"name\": \"color\"}}, \"name\": \"nus_member\", \"order\": {\"array\": []}}"}

"""
