# this project turns Google Keep Exported Jsons to Zoho imported versions
# both have html/json structure. 
from fileinput import filename
import os
import shutil
from turtle import update
from bs4 import BeautifulSoup
import json
import base64
import datetime
# path_to_json+json_files[i]
def load_json_from_path(path_of_json):
  # Opening JSON file
  try:
    f = open(path_of_json)
  except OSError as e:
    f = open(path_of_json, 'w')
  # returns JSON object as
  # a dictionary
  
  try:
    data = json.load(f)
  except:
    data = []
  return data
# print(data
def get_html_in_path(path_to_html):
  json_files = [pos_json for pos_json in os.listdir(path_to_html) if pos_json.endswith('.html')]
  # list_with_path = [path_to_html+ls for ls in json_files] # using list comprehension
  list_with_path = [''+ls for ls in json_files] # using list comprehension
  
  # print(list_with_path[44])
  return list_with_path
  # print(json_files)  # for me this prints ['foo.json']

def remove_html_markup(s):
    tag = False
    quote = False
    out = ""
    for index, c in enumerate(s):
      if c == '<' and not quote:
        tag = True
      elif c == '>' and not quote:
        tag = False
      elif (c == '"' or c == "'") and tag:
        quote = not quote
      elif not tag:
        out = out + c
        # print(out)
    return out

# print(get_html_in_path('carnet/'))
path = 'carnet/'
keep_path = 'keep/'
file_names = get_html_in_path(path)


try:
    os.mkdir(keep_path)
except:
    shutil.rmtree(keep_path)
    os.mkdir(keep_path)

for file_name in file_names:
  # get html data
  page = open(path+file_name, encoding='utf-8')
  soup = BeautifulSoup(page.read(),features="html.parser")
  edit_zones = soup.select("div.edit-zone")

  edit_zone_texts = []
  attached_images = []
  for edit_zone in edit_zones:
    edit_zone_texts.append(str(edit_zone))
    
    if len(edit_zone.select('img')) > 0:
      attached_images.append(edit_zone.select('img'))
  
  edit_zones_text = ''.join(edit_zone_texts)
  
  # print(edit_zones_text)
  
  attachments = []
  attached_images_html = ''
  for attached_image in attached_images:
    image_name = ''
    try:
      image_name = attached_image[0]['src'].split('/')[-1]
      attachments.append({ "filePath": image_name, "mimetype": "image/jpeg" })
    except:
      pass
    # [X] move file to /keep folder + add 
    try:
      shutil.copy(f'{path}data/{image_name}', "keep/"+image_name)
    except FileNotFoundError as e:
      print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

    # [ ] create base 64 image for html of keep file
    encoded_image = ''
    with open(f'{path}data/{image_name}', "rb") as img_file:
      encoded_image = base64.b64encode(img_file.read())
      # decoded_image = encoded_image.decode()    
    attached_image_html = f"""<li><img alt="" src="data:image/jpeg;base64,{encoded_image.decode('utf-8')}"></li>"""
    attached_images_html = attached_images_html + attached_image_html
  
  title = file_name.split(".")[0]
  content_for_json = remove_html_markup(edit_zones_text)
  content_for_html = content_for_json.replace('\n', '<br>')
  # print(title,content)
  

  #get json data 
  karnet_json = load_json_from_path(path+title+".json")
  
  labels = karnet_json['keywords'] 
  labels_html = ''

  #put labels_html inside class="chip label"
  for label in labels:
    label_html = f"""<span class="chip label"><span class="label-name">{label}</span></span>"""
    labels_html = labels_html + label_html
  

  todolists = karnet_json['todolists']
  todos = []
  done_todos = []
  for todolist in todolists:
    todos.extend(todolist['todo'])
    done_todos.extend(todolist['done'])
  list_content = []
  list_content_html = ''
  for todo in todos:
    list_content.append({'text':f'{todo}','isChecked':False})
    list_content_html = list_content_html + f"""<li class="listitem"><span class="bullet">&#9744;</span>
      <span class="text">{todo}</span></li>"""
  for done_todo in done_todos:
    list_content.append({'text':f'{todo}','isChecked':True})
    list_content_html = list_content_html + f"""<li class="listitem checked"><span class="bullet">&#9745;</span>
      <span class="text">{todo}</span></li>"""
  
  if list_content_html != '':
    list_content_html = f"""<ul class="list">{list_content_html}</ul>"""
  else:
    list_content_html = "<br>"

  update_date = karnet_json['last_modification_date']
  created_date = karnet_json['creation_date']
  
  # 2019-09-21T11_54_41.190+03_00.html
  date_as_a_name = datetime.datetime.fromtimestamp(int(created_date)/1000).strftime("%Y-%m-%dT%H_%M_%S0+03_00")
  
  if "untitled" in title:
    title = ""
  # JSON WORK
  keep_json = {}
  # attachments
  keep_json['attachments'] = attachments
  # textContent
  keep_json['textContent'] = content_for_json
  # listContent
  keep_json['listContent'] = list_content
  # title
  keep_json['title'] = title
  # userEditedTimestampUsec
  keep_json['userEditedTimestampUsec'] = update_date * 1000
  # createdTimestampUsec
  keep_json['createdTimestampUsec'] = created_date * 1000
  keep_json['color'] = "DEFAULT",
  keep_json['isTrashed'] = False,
  keep_json['isPinned'] = False,
  keep_json['isArchived'] = False,

  # HTML WORK
  page = open('keep_html_template.html')
  template_soup = BeautifulSoup(page.read(),"html.parser")
  chips_element = template_soup.select_one('div.chips')
  content_element = template_soup.select_one('div.content')
  title_element = template_soup.select_one('title')
  title_class = template_soup.select_one('.title')
  attachments_element =  template_soup.select_one('.attachments').select_one('ul')
  # normalize html
  labels_html = BeautifulSoup(labels_html, "html.parser")
  content_for_html = BeautifulSoup(content_for_html, "html.parser")
  attached_images_html = BeautifulSoup(attached_images_html, "html.parser")
  list_content_html = BeautifulSoup(list_content_html, "html.parser")
  # add to template html
  title_element.string = title # title added to <title> html
  title_class.string = title # title added to class="title" html
  chips_element.append(labels_html) # labels added to html
  content_element.append(content_for_html) # content added to html
  attachments_element.append(attached_images_html) # attachments added to html
  content_element.append(list_content_html) # list content added to html

  # [ ] add date to html? 
  if title == "":
    filename_n = date_as_a_name
  else:
    filename_n = title
  with open('keep/'+filename_n+'.html', "w", encoding="utf16") as file:
    # file.write(str(template_soup))
    file.write(str(template_soup).replace(u'\xa0', u'<br>'))
  with open('keep/'+filename_n+'.json', 'w', encoding='utf8') as outfile:  
    json.dump(keep_json, outfile, ensure_ascii=False)

  print(f'{filename_n} done.')



  # print(template_soup)
  # filename = "asd.txt"
  # with open(filename, 'w',encoding='utf8') as outfile:  
  #   outfile.write(note_text)
    # json.dump(note_text, outfile, ensure_ascii=False)

folder_time = datetime.datetime.now().strftime("%d-%m-%Y_%Hh%Mm%Ss")
shutil.make_archive(folder_time, 'zip', 'keep')
