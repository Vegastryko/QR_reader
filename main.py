import os
import cv2
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import csv
import operator
import time
codec = 'ISO-8859-1'  # or latin-1

def export_metadata(imagename):
    # read the image data using PIL
    image = Image.open(imagename)

    exif_dict = piexif.load(image.info.get('exif'))
    exif_dict = exif_to_tag(exif_dict)

    try:
        longitude = exif_dict['GPS']['GPSLongitude'][2][0]
        latitude  = exif_dict['GPS']['GPSLatitude'][2][0]
    except:
        longitude = '-'
        latitude = '-'

    date = exif_dict['Exif']['DateTimeOriginal']

    return date[11:16], latitude, longitude



def exif_to_tag(exif_dict):
    exif_tag_dict = {}
    thumbnail = exif_dict.pop('thumbnail')
    exif_tag_dict['thumbnail'] = thumbnail.decode(codec)

    for ifd in exif_dict:
        exif_tag_dict[ifd] = {}
        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(codec)

            except AttributeError:
                element = exif_dict[ifd][tag]

            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict

def read_qr_code(filename,scaling):

    try:
        img = cv2.imread(filename)

        scale_percent = scaling # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        value, points, straight_qrcode = cv2.QRCodeDetector().detectAndDecode(resized)
        return value
    except:
        return -1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    tags_catalog = []

    pathstrings_u = ["RC:\Sensoneo\Sledovacka 220728/Processing/Right unprocessed",
                   "LC:\Sensoneo\Sledovacka 220728/Processing/Left unprocessed"]

    pathstrings = ["RC:\Sensoneo\Sledovacka 220728/Processing/Right processed",
                   "LC:\Sensoneo\Sledovacka 220728/Processing/Left processed"]

    # for iter in range(2):
    #     for root, dirs, files in os.walk(pathstrings_u[iter][1:]):
    #         for file in files:
    #             print(os.path.join(root, file))
    #             QR_Code = read_qr_code(os.path.join(root, file),80)
    #             print(QR_Code)
    #             if len(QR_Code)>6:
    #                 os.renames(os.path.join(root, file),pathstrings[iter][1:]+"/"+str(QR_Code)+".jpg")


    for pathstring in pathstrings:
        for root, dirs, files in os.walk(pathstring[1:]):
            for file in files:
                tag = {
                    "Side": None,
                    "ID": None,
                    "Time": None,
                    "Lat": None,
                    "Long": None
                }
                if (str(file)[0:5] == '20000'):
                    tag["Side"] = pathstring[0:1]
                    tag["ID"] = str(file)[:12]
                    tag["Time"] = str(export_metadata(os.path.join(root, file))[0]) +":00"
                    tag["Lat"] = export_metadata(os.path.join(root, file))[1]
                    tag["Long"] = export_metadata(os.path.join(root, file))[2]
                    tags_catalog.append(tag)

    #print(tags_catalog[0].get('Time', None))

    sorted_tags = sorted(tags_catalog, key=lambda t: t['Time'])


    with open('tags_catalog.csv', 'w',newline='') as csv_file:
        fields = ["Side","ID","Time","Lat","Long"]

        csv_writer = csv.DictWriter(csv_file,fields, delimiter=';')
        csv_writer.writeheader()
        for tag in sorted_tags:
            csv_writer.writerow(tag)
        csv_file.close()

