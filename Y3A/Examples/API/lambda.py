import json
import inspect

db = [
  {
    "id": 1,
    "title": "Becoming",
    "author": "Michelle Obama",
    "price": 22.99 
  },
  {
    "id": 2,
    "title": "Humans of New York",
    "author": "Brandon Stanton",
    "price": 19.99 
  }  
]

def response(body, status_code=200, as_html=False):
    res = {
        'statusCode': status_code,
        'body': (body if type(body) == str else json.dumps(body))
    }

    if as_html:
      res['headers'] = {
        'Content-Type': 'text/html'
      }
    else:
      res['headers'] = {
        "Access-Control-Allow-Origin": "*",  # Allow requests from any origin
        "Access-Control-Allow-Credentials": True  # Allow credentials (e.g., cookies) to be sent with the request
      }

    return res

def get_functions():
    return {key: value for key, value in inspect.getmembers(__import__(__name__)) if inspect.isfunction(value)}

# Custom Handlers

def hello_get_handler(event, context):
    return response('Hello World!')

def event_get_handler(event, context):
    return response(event)
    
def context_get_handler(event, context):
    return response(str(context))
    
def array_get_handler(event, context):
    return response(["theese", "are", "many", "strin"])
    
def books_get_handler(event, context):
    try:
      id = int(event['queryStringParameters']['id'])
    except:
      id = 0
      
    if (id > 0):
      for book in db:
        if book["id"] == id:
          return response(book)
      return response(f'Book with id {id} not found', 404)

    return response(db)

# Default handlers

def invalidpath_handler(event, context):
    return response(f"Invalid query:\nPath: {event['path']}\nMethod: {event['httpMethod']}")

def root_get_handler(event, context):
    html_list = '<ul>'
    for name in get_functions():
        core, tail = tuple(name.rsplit('_', 1)) if '_' in name else (name, "")
        if core == "" or core == "lambda" or core == "invalidpath" or tail != "handler":
           continue
        resource, method = tuple(core.rsplit('_', 1)) if '_' in core else (core, "")
        if resource == "root" or (method != "get" and method != "post"):
           continue
        html_list += f'<li><a href="/{resource}">{resource}.{method}</a></li>'
    html_list += '</ul>'
    return response(html_list, 200, True)

def lambda_handler(event, context):
    if "path" not in event:
       return response(event, 400)

    func = event['path'][1:]
    func = func.replace('/', '_')
    func = "root" if func == "" else func
    func += "_"
    func += event['httpMethod'].lower() + "_"
    func += "handler"

    functions = get_functions()
    handler = functions[func] if func in functions else invalidpath_handler

    return handler(event, context)
