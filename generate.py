#!/usr/bin/python3

import json, tarfile, os, io

print("Get your indexers.json from: http://your_jackett_server/api/v2.0/indexers")

with open('indexers.json', encoding='utf-8') as json_file:
    indexers = json.load(json_file)

    if not os.path.isdir("dlm"):
        os.mkdir("dlm") 

    for ind in indexers:
        cid = ind["id"]
        gid = cid.capitalize()
        name = ind["name"]
        site = ind["site_link"]
        className = f"SynoDLMSearch{gid}Jackett"

        info = {
            "name": cid,
            "displayname": name,
            "description": f"{name} via Jackett",
            "version": "1.0",
            "accountsupport": True,
            "site": site,
            "module": "search.php",
            "type": "search",
            "class": className
        }
        infoStr = json.dumps(info, indent=4)

        tarInfo = tarfile.TarInfo('INFO')
        tarInfo.size = len(infoStr)

        searchCode = """<?php

/**
 * Synology search class
 */
class """ + className + """
{
  public $debug = FALSE;
  private $qurl = 'http://<host>/api/v2.0/indexers/""" + cid + """/results/torznab/api?apikey=<apikey>&t=search&cat=&q=<query>';

  /**
   * synology hook
   *
   * @param $curl
   * @param $query
   * @param $username
   * @param $password
   */
  public function prepare($curl, $query, $username = '', $password = '')
  {

    // Strip protocols from the setting.
    $username = strtr($username, [
      'http://' => '',
      'https://' => '',
    ]);

    $url = strtr($this->qurl, [
      '<host>' => trim($username, ' /'),
      '<apikey>' => urlencode(trim($password)),
      '<query>' => urlencode(trim($query)),
    ]);

    if ($this->debug) {
      error_log("REQUEST: {$url}");
    }

    // Setup the $curl handler.
    curl_setopt($curl, CURLOPT_URL, $url);
  }

  /**
   * synology hook
   *
   * @param $plugin
   * @param $response
   *
   * @return int
   */
  public function parse($plugin, $response)
  {
    $count = 0;

    $xml = simplexml_load_string(trim($response), 'SimpleXMLElement');

    if (empty($xml->channel)) {
      return $count;
    }
    
    foreach ($xml->channel->item as $child) {

      $peers = $child->xpath('torznab:attr[@name="peers"]')
        ? (int)$child->xpath('torznab:attr[@name="peers"]')[0]['value']
        : 0;

      $seeders = $child->xpath('torznab:attr[@name="seeders"]')
        ? (int)$child->xpath('torznab:attr[@name="seeders"]')[0]['value']
        : 0;

      $categories = [];
      foreach ($child->xpath('torznab:attr[@name="category"]') as $category) {
        $categories[] = $category['value'];
      }

      $leechs = $peers ? $peers - $seeders : 0;
      $title = urldecode((string) $child->title);
      $download = (string) $child->link;
      $size = (double) $child->size;
      $datetime = date('Y-m-d H:i:s', strtotime($child->pubDate));
      $page = (string) $child->comments;
      $hash = md5($count . $download);

      $plugin->addResult($title, $download, $size, $datetime, $page, $hash, $seeders, $leechs, array_shift($categories));

      $count++;
    }

    return $count;
  }

  /**
   * synology hook
   *
   * @param $username
   * @param $password
   *
   * @return bool
   */
  public function VerifyAccount($username, $password)
  {

    $curl = curl_init();
    curl_setopt_array($curl, [
      CURLOPT_RETURNTRANSFER => TRUE,
      CURLOPT_SSL_VERIFYHOST => FALSE,
      CURLOPT_SSL_VERIFYPEER => FALSE,
      CURLOPT_TIMEOUT => 20,
      CURLOPT_FOLLOWLOCATION => TRUE,
      CURLOPT_USERAGENT => 'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
    ]);

    $this->prepare($curl, '', $username, $password);

    $result = curl_exec($curl);
    $httpcode = curl_getinfo($curl, CURLINFO_HTTP_CODE);

    curl_close($curl);

    if (strpos($result, 'Invalid API Key') !== false) {
      return false;
    }

    return (int) $httpcode == 200;
  }

}
"""
        tarSearch = tarfile.TarInfo('search.php')
        tarSearch.size = len(searchCode)

        with tarfile.open(f'dlm/{gid}-Jackett.dlm', 'w:gz') as tar:
            tar.addfile(tarInfo, io.BytesIO(infoStr.encode('utf8')))
            tar.addfile(tarSearch, io.BytesIO(searchCode.encode('utf8')))

        print(f"{cid} - {name}")