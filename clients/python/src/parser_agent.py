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
from sensei_client import BQLRequest, SenseiClient, SenseiClientError, SenseiRequest
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

      variables = re.findall(r"\$[a-zA-Z0-9]+", info["bql"])
      variables = list(set(variables))
      info["auxParams"] = {"array": [ {"name": var[1:]} for var in variables ]}

      req = BQLRequest(info["bql"])
      result = json.dumps(req.construct_ucp_json(info))

      return json.dumps(
        {
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

def construct_ucp_json(request, info):
  """Construct BQL query template for UCP."""

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

  # input = {
  #   "name": "nus_member",
  #   "description": "xxx xxx",
  #   "urn": "urn:feed:nus:member:exp:a:$memberId",
  #   "bql": "select * from ..."
  #   },

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
      }
    }

  return json.dumps(output)


def main(argv):
  from optparse import OptionParser
  usage = "usage: %prog [options]"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--interactive", dest="interactive",
                    default=False, help="Run UCP parser in interactive mode")
  parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    default=False, help="Turn on verbose mode")
  (options, args) = parser.parse_args()

  if options.verbose:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)d - %(message)s")
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  # if len(args) <= 1:
  #   client = SenseiClient()
  # else:
  #   host = args[0]
  #   port = int(args[1])
  #   logger.debug("Url specified, host: %s, port: %d" % (host,port))
  #   client = SenseiClient(host, port, 'sensei')

  def test_ucp(stmt):
    # test(stmt)
    req = BQLRequest(stmt)

    info = {
      "name": "nus_member",
      "description": "xxx xxxx",
      "urn": "urn:feed:nus:member:exp:a:$memberId",
      "auxParams" : {"array": [ {"name": "var1"} ]},
      "bql": stmt
      }
    print construct_ucp_json(req, info)

  import readline
  readline.parse_and_bind("tab: complete")
  while 1:
    try:
      stmt = raw_input('> ')
      if stmt == "exit":
        break
      # if options.verbose:
      #   test(stmt)
      req = SenseiRequest(stmt)
      # if req.stmt_type == "select":
      #   res = client.doQuery(req)
      #   res.display(columns=req.get_columns(), max_col_width=int(options.max_col_width))
      # elif req.stmt_type == "desc":
      #   sysinfo = client.getSystemInfo()
      #   sysinfo.display()
      # else:
      #   pass
      # test_sql(stmt)
      test_ucp(stmt)
    except EOFError:
      break
    except ParseException as err:
      print " " * (err.loc + 2) + "^\n" + err.msg
    except SenseiClientError as err:
      print err

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
