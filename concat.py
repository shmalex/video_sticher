#!/usr/bin/env python

import glob
from PIL import Image, ImageFont, ImageDraw
import os
import sys
import tqdm
import shutil
import subprocess
import datetime


import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


import io


def get_date(path):
    img = Image.open(path)
    if img._getexif() is None:
        return ''
    return img._getexif()[306]


title_font = ImageFont.truetype('cour.ttf', 30)
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.readonly']

if __name__ == "__main__":
    base_dir = sys.argv[1]
    folder_id = sys.argv[2]
    dest_dir = os.path.join(base_dir, '..', 'renamed')
    print('Input:', base_dir)
    if not os.path.exists(base_dir):
        print('Path does not exists', base_dir)
        os.makedirs(base_dir, exist_ok=True)
        print('Path created', base_dir)

    files = glob.glob(base_dir+'*.jpg')
    print("Total images found", len(files), "sample:")
    print('\n'.join(files[:5]))
    os.makedirs(dest_dir, exist_ok=True)

    files = list(filter(lambda x: os.path.getsize(x) > 5*10**5, files))
    print("Total after filtering", len(files))
    print('Sorting...')
    files = list(sorted(files, key=lambda x: get_date(x)))

    ##################### GDrive Credentials
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        valid = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                valid = True
            except Exception as re:
                print(re)
                valid = False
        if not valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_2.json', SCOPES)
            creds = flow.run_local_server(host="localhost", port=8070)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    ##################### GDrive download
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if len(files) > 0:
        img = Image.open(files[-1])
        dt = img._getexif()[306]
        date, time = dt.split(' ')
        date = date.replace(':', '-')
        dt = datetime.datetime.fromisoformat(date + ' ' + time)
        search_dt = (dt + (datetime.datetime.utcnow() -
                           datetime.datetime.now())).isoformat()
    else:
        search_dt = datetime.datetime(1990, 1, 1, 1, 1, 1).isoformat()

    service = build('drive', 'v3', credentials=creds)

    page_token = None
    print('Search Date', search_dt)
    while True:
        # Call the Drive v3 API
        results = service.files().list(
            pageSize=100,
            fields="nextPageToken, files(*)",
            q=f"'{folder_id}' in parents  and createdTime > '{search_dt}' " +
            " and mimeType='image/jpeg'",
            orderBy="name",
            pageToken=page_token).execute()
        items = results.get('files', [])
#         print('page_token',page_token)
        if not items:
            print('No files found.')
        with tqdm.tqdm(items) as tq:
            for item in tq:
                tq.set_description(desc=u'{2} {0} ({1})'.format(
                    item['name'], item['id'], item['createdTime']), refresh=True)
                file_id = item['id']
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                f = open(os.path.join(base_dir, item['name']), 'wb')
                f.write(fh.getbuffer())
                f.close()
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break

    ##################### Reload Files

    files = glob.glob(base_dir+'*.jpg')
    print("Total images found", len(files), "sample:")
    print('\n'.join(files[:5]))
    os.makedirs(dest_dir, exist_ok=True)

    files = list(filter(lambda x: os.path.getsize(x) > 5*10**5, files))
    print("Total after filtering", len(files))
    print('Sorting...')
    files = list(sorted(files, key=lambda x: get_date(x)))

    ##################### Get exif from renamed file

    ren_files = glob.glob(dest_dir+'/*.jpg')
    print('Total Renamed Images', len(ren_files))
    created = {get_date(ren_file): os.path.basename(ren_file)
               for ren_file in ren_files}

    ##################### Rename Files, add timestamp

    n = 7  # len(str(len(files)))+1
    print("name pattern", f'{0:0{n}}.jpg')

    for i, file in enumerate(tqdm.tqdm(files, desc='coping')):
        img = Image.open(file)
        title_text = img._getexif()[306]
        file_name = f'{i:0{n}}.jpg'
        if title_text in created:
            if created[title_text] == file_name:
                continue
        exif = img.info['exif']
        image_editable = ImageDraw.Draw(img)
        image_editable.rectangle((10, 15, 360, 46), fill="#444444")
        image_editable.text((15, 15), title_text,
                            (255, 255, 255), font=title_font)
        img.save(os.path.join(dest_dir, file_name), exif=exif)

#         shutil.copyfile(file, os.path.join(dest_dir, f'{i:0{n}}.jpg'))

    if False:
        for i, file in enumerate(tqdm.tqdm(files, desc='coping')):
            shutil.copyfile(file, os.path.join(dest_dir, f'{i:0{n}}.jpg'))
    if False:
        angle = -90
        for i, file in enumerate(files):
            print(f"{i:04}")
            img = PIL.Image.open(file)
            out = img.rotate(angle, expand=True)
            out.save(os.path.join('./renamed', f'{i:0n}.jpg'))
    print("Done renaming")
    print('Exit')
