
What is Rapic ?
===============
Rapic is a simple and fast lightweight tool for automatically generating api client libraries and sdk for websites and online services. It also support 
automatic generation of client libraries for 3rd party public and private api's which is very good for reverse engineers.

Installation
==============
pip install rapic

Running
========

  There are 2 ways to use rapic
 - Using rapic-client-generator to automatically generate client file from a reverse engineering tool.
 - Manually creating rapic api client file.


Using Rapic Client Generator
======================
As a reverse engineer saving time is essential which means reducing time spent on writing 
api client for reversed private 3rd party api, website or other internet services. Rapic makes generating
 client libraries easy with just these few steps :
 
** NOTE** 
Rapic automatic client generator only support BURPSUITE reverse engineering tool currently
 
 - STEP 1 : While using BurpSuite Right click on a website under site map tab under target
 - STEP 2 : Save requests as xml file and untick base64 encode requests and response
 - STEP 3 : Run 'rapic-client-generator burp <website_site_or_api_name> saved_file.xml'
 - STEP 4 : Open generated json file and name your request then Use the client like
 
          from rapic.client import APIClient
          api = ApiClient(client_name='website_or_service_name', request_file=generated_file_from_rapic.json)
          val = api.get_currency() # A request is named get_currency by changing request_<num> to get_currency for a chosen request in json file
    
 Using Rapic Client JSON files
======================    
  Programmers can also save time when creating client libraries/sdk for their website and service using rapic. Simply by
  creating a json file with structure
    
    ***json_file.json  
    
                {
                 "host": "httpbin.org",
                  "scheme": "http",
                      "get_my_ip": {
                            "path": "/ip",
                            "method": "GET"
                        },
                 }
                    
                    
     *** client.py
     
          from rapic.client import APIClient
          api = ApiClient(client_name='website_or_service_name', request_file=json_file.json)
          val = api.get_my_ip() 
  
  NOTE : check test folder for more json file structure and supported keys
  
  Request can also be hooked before its sent to server to do extra processing like http signature signing, timestamp generation etc.
  
  
   
        ***json_file.json 
        
                {
                 "host": "httpbin.org",
                  "scheme": "http",
                      "get_user_followers": {
                            "path": "/get_user_followers/{path_id}",
                            "method": "POST"
                        },
                 }
         ***client.py
         
            import hashlib
            from rapic.client import APIClient
            from rapic.hook import APIClientHook
            
            class MyApiClient(APIClient):

                @APIClientHook.hook_client_request_data(client='httpbin',
                                                        requests=['get_user_followers'])
                def set_http_signature_on_header(data, **kwargs):
                    sign_request = data['url'] + data['method'] + urlencode(data['body_data'])
                    m = hashlib.sha256()
                    m.update(bytes(sign_request, encoding='utf8'))
                    signature = m.hexdigest()
                    data['headers']['signature'] = signature
                    self.http_signature = signature
                    return data
            api = MyApiClient(client_name='website_or_service_name', request_file=json_file.json)
            val = api.get_user_followers(data={user_id : 67888}, url_data={path_id : 'unique_id_get_set_as_path_id'})
     
     
     
**  List of hooks supported **
  
- APIClientHook.hook_client_prepared_request()
- APIClientHook.hook_client_response()
- APIClientHook.hook_client_request_data()
- APIClientHook.hook_client_body_data()
- APIClientHook.hook_client_url()
- APIClientHook.hook_client_header()
                 
                    
  
    
**LICENSE**
=========
MIT
                    
     
     
                    
                    
                  
                  
    