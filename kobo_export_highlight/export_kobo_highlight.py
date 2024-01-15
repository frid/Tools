#%% 
import sqlite3
import tempfile
import shutil
from pprint import pprint

#%% parse argument
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("db_path", help="Path to kobo.sql (Example: \"/path/to/Kobo.sqlite\")", default=None)
parser.add_argument("out_csv_path", help="Path to output .csv file (Default: ./test.csv)", default=None)
parser.add_argument("--encode", help="file encoding (Default: cp950)", default="cp950")
args = parser.parse_args()
print("db_path: ", args.db_path)
print("out_csv_path: ", args.out_csv_path)

import sys


#%%
tmp_dir = tempfile.gettempdir()
if (args.db_path==None):
  src_db_path = "/mnt/c/Users/fridh/AppData/Local/Kobo/Kobo Desktop Edition/Kobo.sqlite"
else:
  src_db_path = args.db_path
db_path = tmp_dir + "/Kobo.sqlite"
shutil.copy(src_db_path, db_path)


conn = sqlite3.connect(db_path)
cursor = conn.cursor()

#%% List Books
sql_cmd = '''
SELECT 
ContentID as BOOKID,
ISBN, title
FROM content WHERE contenttype=6 AND Accessibility=1 
order by DateLastRead DESC;
'''

res = cursor.execute(sql_cmd)
result = res.fetchall()
pprint(result)

#%% Query highlights from ISBN
sql_cmd = '''
SELECT 
Bookmark.ContentID, Bookmark.DateCreated, ISBN, title, text, annotation
from bookmark
left outer join content
on (content.contentID=bookmark.VolumeID and content.ContentType=6)
where  
text is not null and
ISBN is '9789865596941'
'''

res = cursor.execute(sql_cmd)
result = res.fetchall()
pprint(result)
# %%
import pandas as pd
df = pd.DataFrame(result)
df[1] = pd.to_datetime(df[1])
print(df)
# %% update highlight chapter number
chapter_ids = list(set(df[0]))
chapter_name = []

for id in chapter_ids:
  sql_cmd = '''
  SELECT title from content
  where
  chapterIDBookmarked is '{}'
  '''.format(id)

  res = cursor.execute(sql_cmd)
  result = res.fetchall()
  chapter_name = result[0][0].replace(u'\u3000',u'').replace('\n', '').replace('\r', '').replace(" ","")
  print(chapter_name)
  df[0].replace(id, chapter_name, inplace=True)

# %%
csv_path = []
if args.out_csv_path == None:
  csv_path = "./test.csv"
else:
  csv_path = args.out_csv_path

file_encoding = "cp950"
if not args.encoding:
  file_encoding = args.encoding

df.to_csv(csv_path, encoding=file_encoding)