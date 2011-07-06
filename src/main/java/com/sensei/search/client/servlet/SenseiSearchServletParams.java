package com.sensei.search.client.servlet;

public interface SenseiSearchServletParams {
	public static final String PARAM_OFFSET = "start";
	public static final String PARAM_COUNT = "rows";
	public static final String PARAM_QUERY = "q";
	public static final String PARAM_QUERY_PARAM = "qparam";
	public static final String PARAM_SORT = "sort";
	public static final String PARAM_SORT_ASC = "asc";
	public static final String PARAM_SORT_DESC = "desc";
	public static final String PARAM_SORT_SCORE = "relevance";
	public static final String PARAM_SORT_SCORE_REVERSE = "relrev";
	public static final String PARAM_SORT_DOC = "doc";
	public static final String PARAM_SORT_DOC_REVERSE = "docrev";
	public static final String PARAM_FETCH_STORED = "fetchstored";
	public static final String PARAM_SHOW_EXPLAIN = "showexplain";
	public static final String PARAM_ROUTE_PARAM = "routeparam";
	public static final String PARAM_GROUP_BY = "groupby";
	public static final String PARAM_SELECT = "select";
	public static final String PARAM_SELECT_VAL = "val";
	public static final String PARAM_SELECT_NOT = "not";
	public static final String PARAM_SELECT_OP = "op";
	public static final String PARAM_SELECT_OP_AND = "and";
	public static final String PARAM_SELECT_OP_OR = "or";
	public static final String PARAM_SELECT_PROP = "prop";
	public static final String PARAM_FACET = "facet";
	public static final String PARAM_DYNAMIC_INIT = "dyn";
	public static final String PARAM_PARTITIONS = "partitions";

	public static final String PARAM_FACET_EXPAND = "expand";
	public static final String PARAM_FACET_MAX = "max";
	public static final String PARAM_FACET_MINHIT = "minhit";
	public static final String PARAM_FACET_ORDER = "order";
	public static final String PARAM_FACET_ORDER_HITS = "hits";
	public static final String PARAM_FACET_ORDER_VAL = "val";

	public static final String PARAM_DYNAMIC_TYPE = "type";
	public static final String PARAM_DYNAMIC_TYPE_STRING = "string";
	public static final String PARAM_DYNAMIC_TYPE_BYTEARRAY = "bytearray";
	public static final String PARAM_DYNAMIC_TYPE_BOOL = "boolean";
	public static final String PARAM_DYNAMIC_TYPE_INT = "int";
	public static final String PARAM_DYNAMIC_TYPE_LONG = "long";
	public static final String PARAM_DYNAMIC_TYPE_DOUBLE = "double";
	public static final String PARAM_DYNAMIC_VAL = "vals";

	public static final String PARAM_RESULT_PARSEDQUERY = "parsedquery";
	public static final String PARAM_RESULT_HIT_STORED_FIELDS = "stored";
	public static final String PARAM_RESULT_HIT_STORED_FIELDS_NAME = "name";
	public static final String PARAM_RESULT_HIT_STORED_FIELDS_VALUE = "val";
	public static final String PARAM_RESULT_HIT_EXPLANATION = "explanation";
	public static final String PARAM_RESULT_HIT_GROUPVALUE = "groupvalue";
	public static final String PARAM_RESULT_HIT_GROUPHITSCOUNT = "grouphitscount";
	public static final String PARAM_RESULT_FACETS = "facets";

	public static final String PARAM_RESULT_TID = "tid";
	public static final String PARAM_RESULT_TOTALDOCS = "totaldocs";
	public static final String PARAM_RESULT_TOTALGROUPS = "totalgroups";
	public static final String PARAM_RESULT_NUMHITS = "numhits";
	public static final String PARAM_RESULT_NUMGROUPS = "numgroups";
	public static final String PARAM_RESULT_HITS = "hits";
	public static final String PARAM_RESULT_HIT_UID = "uid";
	public static final String PARAM_RESULT_HIT_DOCID = "docid";
	public static final String PARAM_RESULT_HIT_SCORE = "score";
	public static final String PARAM_RESULT_HIT_SRC_DATA = "srcdata";
	public static final String PARAM_RESULT_TIME = "time";

	public static final String PARAM_SYSINFO_NUMDOCS = "numdocs";
	public static final String PARAM_SYSINFO_LASTMODIFIED = "lastmodified";
	public static final String PARAM_SYSINFO_VERSION = "version";
	public static final String PARAM_SYSINFO_FACETS = "facets";
	public static final String PARAM_SYSINFO_FACETS_NAME = "name";
	public static final String PARAM_SYSINFO_FACETS_RUNTIME = "runtime";
	public static final String PARAM_SYSINFO_FACETS_PROPS = "props";
	public static final String PARAM_SYSINFO_CLUSTERINFO = "clusterinfo";
	public static final String PARAM_SYSINFO_CLUSTERINFO_ID = "id";
	public static final String PARAM_SYSINFO_CLUSTERINFO_PARTITIONS = "partitions";
	public static final String PARAM_SYSINFO_CLUSTERINFO_NODELINK = "nodelink";
	public static final String PARAM_SYSINFO_CLUSTERINFO_ADMINLINK = "adminlink";

	public static final String PARAM_RESULT_HITS_EXPL_VALUE = "value";
	public static final String PARAM_RESULT_HITS_EXPL_DESC = "description";
	public static final String PARAM_RESULT_HITS_EXPL_DETAILS = "details";

	public static final String PARAM_RESULT_FACET_INFO_VALUE = "value";
	public static final String PARAM_RESULT_FACET_INFO_COUNT = "count";
	public static final String PARAM_RESULT_FACET_INFO_SELECTED = "selected";
}
