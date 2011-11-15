import sys
import unittest
import json

sys.path.insert(0, "../src")
import sensei_client
from sensei_client import *
from pyparsing import ParseException
import parser_agent

class TestUCPQueryTemplate(unittest.TestCase):
  """Test cases for UCP query template."""

  def testBasics(self):
    stmt = \
        "SELECT color, year FROM cars WHERE QUERY IS 'cool $myKeywords' AND year < 1996 GIVEN FACET PARAM (My-Network, 'srcid', int, '$memberId'), (My-Network, 'metaData', string, 'myMetaData') ORDER BY color GROUP BY color TOP 15;"

    info = {
      "name": "nus_member",
      "description": "Test BQL query template generator",
      "urn": "urn:feed:nus:member:exp:a:$memberId",
      "bql": stmt
      }

    # print json.dumps(parser_agent.construct_ucp_json(info), sort_keys=True, indent=4)

    self.assertEqual(json.dumps(parser_agent.construct_ucp_json(info),
                                sort_keys=True, indent=4),
                     """{
    "bqlQueryInfo": {
        "bql": "SELECT color, year FROM cars WHERE QUERY IS 'cool $myKeywords' AND year < 1996 GIVEN FACET PARAM (My-Network, 'srcid', int, '$memberId'), (My-Network, 'metaData', string, 'myMetaData') ORDER BY color GROUP BY color TOP 15;", 
        "fromClause": {
            "array": [
                "cars"
            ]
        }, 
        "selectClause": {
            "array": [
                "color", 
                "year"
            ]
        }
    }, 
    "description": "Test BQL query template generator", 
    "facets": {
        "array": [
            {
                "initParams": {
                    "array": [
                        {
                            "name": "srcid", 
                            "type": "INT", 
                            "values": [
                                "$memberId"
                            ]
                        }, 
                        {
                            "name": "metaData", 
                            "type": "STRING", 
                            "values": [
                                "myMetaData"
                            ]
                        }
                    ]
                }, 
                "name": "My-Network"
            }
        ]
    }, 
    "feedQuery": {
        "auxParams": {
            "array": [
                {
                    "name": "memberId"
                }, 
                {
                    "name": "myKeywords"
                }
            ]
        }, 
        "urn": "urn:feed:nus:member:exp:a:$memberId"
    }, 
    "filters": {
        "com.linkedin.ucp.query.models.QueryFilters": {
            "facetSelections": {
                "array": [
                    {
                        "name": "year", 
                        "selection": {
                            "array": [
                                "[* TO 1995]"
                            ]
                        }, 
                        "valueOperation": "AND"
                    }
                ]
            }, 
            "keywords": {
                "array": [
                    "cool $myKeywords"
                ]
            }
        }
    }, 
    "groupBy": {
        "com.linkedin.ucp.query.models.QueryFacetGroupBySpec": {
            "maxHitsPerGroup": 15, 
            "name": "color"
        }
    }, 
    "name": "nus_member", 
    "order": {
        "array": [
            {
                "name": "color", 
                "sortOrder": "ASC"
            }
        ]
    }
}""")

if __name__ == "__main__":
    unittest.main()
