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
        "SELECT color, year FROM cars WHERE QUERY IS 'cool $myKeywords' AND year < 1996 ORDER BY color GROUP BY color TOP 15;"

    req = BQLRequest(stmt)
    info = {
      "name": "nus_member",
      "description": "Test BQL query template generator",
      "urn": "urn:feed:nus:member:exp:a:$memberId",
      "bql": stmt
      }
    self.assertEqual(parser_agent.construct_ucp_json(req, info),
                     """{
    "bql": "SELECT color, year FROM cars WHERE QUERY IS 'cool $myKeywords' AND year < 1996 ORDER BY color GROUP BY color TOP 15;", 
    "description": "Test BQL query template generator", 
    "facets": {
        "array": []
    }, 
    "feedQuery": {
        "auxParams": {
            "array": [
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
