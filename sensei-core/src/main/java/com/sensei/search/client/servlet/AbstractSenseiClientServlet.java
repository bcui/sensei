package com.sensei.search.client.servlet;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLDecoder;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;

import com.linkedin.norbert.javacompat.cluster.ClusterClient;
import com.linkedin.norbert.javacompat.cluster.ZooKeeperClusterClient;
import com.linkedin.norbert.javacompat.network.NetworkClientConfig;
import com.sensei.search.cluster.client.SenseiNetworkClient;
import com.sensei.search.nodes.SenseiBroker;
import com.sensei.search.nodes.SenseiSysBroker;
import com.sensei.search.nodes.impl.NoopRequestScatterRewriter;
import com.sensei.search.req.SenseiRequest;
import com.sensei.search.req.SenseiResult;
import com.sensei.search.req.SenseiSystemInfo;

public abstract class AbstractSenseiClientServlet extends ZookeeperConfigurableServlet {

  private static final long serialVersionUID = 1L;
  
  private static final Logger logger = Logger.getLogger(AbstractSenseiClientServlet.class);

  private final NetworkClientConfig _networkClientConfig = new NetworkClientConfig();
  
  private ClusterClient _clusterClient = null;
  private SenseiNetworkClient _networkClient = null;
  private SenseiBroker _senseiBroker = null;
  private SenseiSysBroker _senseiSysBroker = null;
  public AbstractSenseiClientServlet() {
  
  }

  @Override
  public void init(ServletConfig config) throws ServletException {
    super.init(config);
    _networkClientConfig.setServiceName(clusterName);
    _networkClientConfig.setZooKeeperConnectString(zkurl);
    _networkClientConfig.setZooKeeperSessionTimeoutMillis(zkTimeout);
    _networkClientConfig.setConnectTimeoutMillis(connectTimeoutMillis);
    _networkClientConfig.setWriteTimeoutMillis(writeTimeoutMillis);
    _networkClientConfig.setMaxConnectionsPerNode(maxConnectionsPerNode);
    _networkClientConfig.setStaleRequestTimeoutMins(staleRequestTimeoutMins);
    _networkClientConfig.setStaleRequestCleanupFrequencyMins(staleRequestCleanupFrequencyMins);
    
    _clusterClient = new ZooKeeperClusterClient(clusterName,zkurl,zkTimeout);
  
    _networkClientConfig.setClusterClient(_clusterClient);
    
    _networkClient = new SenseiNetworkClient(_networkClientConfig, null);
    _senseiBroker = new SenseiBroker(_networkClient, _clusterClient, loadBalancerFactory);
    _senseiSysBroker = new SenseiSysBroker(_networkClient, _clusterClient, loadBalancerFactory, versionComparator);
    
    logger.info("Connecting to cluster: "+clusterName+" ...");
    _clusterClient.awaitConnectionUninterruptibly();

    logger.info("Cluster: "+clusterName+" successfully connected ");
  }
  
  protected abstract SenseiRequest buildSenseiRequest(HttpServletRequest req) throws Exception;

  private void handleSenseiRequest(HttpServletRequest req, HttpServletResponse resp)
    throws ServletException, IOException {
    try {
      SenseiRequest senseiReq = buildSenseiRequest(req);
      SenseiResult res = _senseiBroker.browse(senseiReq);
      OutputStream ostream = resp.getOutputStream();
      convertResult(senseiReq,res,ostream);
      ostream.flush();
    } catch (Exception e) {
      throw new ServletException(e.getMessage(),e);
    }
  }
  
  private void handleSystemInfoRequest(HttpServletRequest req, HttpServletResponse resp)
    throws ServletException, IOException {
    try {
      SenseiSystemInfo res = _senseiSysBroker.browse(new SenseiRequest()); 
      OutputStream ostream = resp.getOutputStream();
      convertResult(res, ostream);
      ostream.flush();
    } catch (Exception e) {
      throw new ServletException(e.getMessage(),e);
    }
  }

  private void handleJMXRequest(HttpServletRequest req, HttpServletResponse resp)
    throws ServletException, IOException
  {
    InputStream is = null;
    OutputStream os = null;
    try
    {
      String myPath = req.getRequestURI().substring(req.getServletPath().length()+11);
      URL adminUrl = null;
      if (myPath.indexOf('/') > 0)
      {
        adminUrl = new URL(new StringBuilder(URLDecoder.decode(myPath.substring(0, myPath.indexOf('/')), "UTF-8"))
          .append("/admin/jmx")
          .append(myPath.substring(myPath.indexOf('/'))).toString());
      }
      else
      {
        adminUrl = new URL(new StringBuilder(URLDecoder.decode(myPath, "UTF-8"))
          .append("/admin/jmx").toString());
      }

      URLConnection conn = adminUrl.openConnection();

      byte[] buffer = new byte[8192]; // 8k
      int len = 0;

      InputStream ris = req.getInputStream();

      while((len=ris.read(buffer)) > 0)
      {
        if (!conn.getDoOutput()) {
          conn.setDoOutput(true);
          os = conn.getOutputStream();
        }
        os.write(buffer, 0, len);
      }
      if (os != null)
        os.flush();

      is = conn.getInputStream();
      OutputStream ros = resp.getOutputStream();

      while((len=is.read(buffer)) > 0)
      {
        ros.write(buffer, 0, len);
      }
      ros.flush();
    }
    catch (Exception e)
    {
      throw new ServletException(e.getMessage(),e);
    }
    finally
    {
      if (is != null)
        is.close();
      if (os != null)
        os.close();
    }
  }
  
  @Override
  protected void doGet(HttpServletRequest req, HttpServletResponse resp)
      throws ServletException, IOException {
    resp.setContentType("application/json; charset=utf-8");
    resp.setCharacterEncoding("UTF-8");

    resp.setHeader("Access-Control-Allow-Origin", "*");
    resp.setHeader("Access-Control-Allow-Methods", "GET, POST");
    resp.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Accept");

    if (null == req.getPathInfo() || "/".equalsIgnoreCase(req.getPathInfo()))
    {
      handleSenseiRequest(req, resp);
    }
    else if ("/sysinfo".equalsIgnoreCase(req.getPathInfo()))
    {
      handleSystemInfoRequest(req, resp);
    }
    else if (req.getPathInfo().startsWith("/admin/jmx/"))
    {
      handleJMXRequest(req, resp);
    }
    else
    {
      handleSenseiRequest(req, resp);
    }
  }
  
  @Override
  protected void doPost(HttpServletRequest req, HttpServletResponse resp)
      throws ServletException, IOException
  {
    doGet(req, resp);
  }
  
  @Override
  protected void doOptions(HttpServletRequest req, HttpServletResponse resp)
      throws ServletException, IOException
  {
    resp.setHeader("Access-Control-Allow-Origin", "*");
    resp.setHeader("Access-Control-Allow-Methods", "GET, POST");
    resp.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Accept");
  }
  
  protected abstract void convertResult(SenseiSystemInfo info, OutputStream ostream) throws Exception;

  protected abstract void convertResult(SenseiRequest req,SenseiResult res,OutputStream ostream) throws Exception;

  @Override
  public void destroy() {
    try{
      try{
        if (_senseiBroker!=null){
          _senseiBroker.shutdown();
          _senseiBroker = null;
        }
      }
      finally{
        try {
          if (_senseiSysBroker!=null){
            _senseiSysBroker.shutdown();
            _senseiSysBroker = null;
          }
        }
        finally
        {
          try{
            if (_networkClient!=null){
              _networkClient.shutdown();
              _networkClient = null;
            }
          }
          finally{
            if (_clusterClient!=null){
              _clusterClient.shutdown();
              _clusterClient = null;
            }
          }
        }
      }
      
    }
    finally{
      super.destroy();
    }
  }
}
