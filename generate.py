#!/bin/python3

import argparse
import sys
import shutil
import os
import os.path
import yaml
import subprocess as sp

CWD = os.getcwd()

IMG_DIR = "/share/backgrounds"
IMG_PATH = IMG_DIR + "/%s.jpg"
XML_DIR = "/share/background-properties"
XML_PATH = XML_DIR + "/%s.xml"

GNOME_XML_DIR = "/share/gnome-background-properties"
GNOME_XML_PATH = GNOME_XML_DIR + "/%s.xml"

MATE_XML_DIR = "/share/mate-background-properties"
MATE_XML_PATH = MATE_XML_DIR + "/%s.xml"

XFCE_IMG_DIR = "/share/backgrounds/xfce"
XFCE_IMG_PATH = XFCE_IMG_DIR + "/%s.jpg"

# A single file named 1x1 to appease KDE
KDE_PATH = "/share/wallpapers/%s"
KDE_IMG_PATH = KDE_PATH + "/contents/images/1x1.jpg"

AUTHORS = "authors.yaml"

with open("desktop.in", "rt") as f:
    DESKTOP_IN = f.read()

with open("xml.in", "rt") as f:
    XML_IN = f.read()


def copy(src, dst):
    shutil.copyfile(src, dst)


def ln(src, dst):
    try:
        os.symlink(dst, src)
    except FileExistsError as e:
        os.remove(src)
        os.symlink(dst, src)


def mkdir(path):
    os.makedirs(path, mode=0o755, exist_ok=True)


def normalize_fname(title):
    return title.replace("\'", "").replace(" ", "_").replace("-", "_")


def xml_escape(string):
    ret = string.replace("&", "&amp;")
    print(ret)
    return ret


def proc_image(subdir, author, title, email, license, dest, prefix):
    print("Author: %s, Image: %s" % (author, title))
    fname = normalize_fname(title)

    # Path to solid output xml, not symlink
    xml_path = (prefix + XML_PATH) % fname
    img_path = (prefix + IMG_PATH) % fname

    # Path to symlinks
    gnome_xml_path = (prefix + GNOME_XML_PATH) % fname
    mate_xml_path = (prefix + MATE_XML_PATH) % fname
    xfce_img_path = (prefix + XFCE_IMG_PATH) % fname
    kde_path = (prefix + KDE_PATH) % fname
    kde_img_path = (prefix + KDE_IMG_PATH) % fname

    # Meta data content
    xml_content = XML_IN.replace("%TITLE%", title) \
            .replace("%FILENAME%", img_path) \
            .replace("%AUTHOR%", xml_escape(author))
    desktop_content = DESKTOP_IN.replace("%TITLE%", title) \
            .replace("%AUTHOR%", author) \
            .replace("%EMAIL%", email) \
            .replace("%LICENSE%", license) \
            .replace("%FNAME%", fname)

    # Install directories
    mkdir(dest + kde_path + "/contents/images")

    # Install base images, xmls
    src_img = subdir + "/" + fname + ".jpg"
    copy(src_img, dest + img_path);
    with open(dest + xml_path, "w") as f:
        f.write(xml_content)

    # Create XML links for Gnome and Mate
    ln(dest + gnome_xml_path, xml_path)
    ln(dest + mate_xml_path, xml_path)

    # Handle KDE
    # Install desktop file and data structure
    with open(dest + kde_path + "/metadata.desktop", "w") as f:
        f.write(desktop_content)
    mkdir(dest + kde_path + "/contents/images")
    ln(dest + kde_img_path, img_path)
    # KDE wants a thumbnail or "screenshot" at /contents/screenshot.png
    sp.run(["convert", src_img, "-resize", "500x500", dest + kde_path + "/contents/screenshot.png"])

def __main__():
    parser = argparse.ArgumentParser(description='Generate data')
    parser.add_argument('--output', '-o', default=".", help="Dest DIR")
    parser.add_argument('--prefix', '-p', default="/usr", help="Prefix DIR")
    arg = parser.parse_args()

    DEST = arg.output
    PREFIX = arg.prefix

    with open(AUTHORS, 'r') as f:
        authors = yaml.full_load(f)

    mkdir(DEST + PREFIX + IMG_DIR)
    mkdir(DEST + PREFIX + XML_DIR)
    mkdir(DEST + PREFIX + GNOME_XML_DIR)
    mkdir(DEST + PREFIX + MATE_XML_DIR)
    mkdir(DEST + PREFIX + XFCE_IMG_DIR)

    for author in authors:
        subdir = CWD + "/" + author["dir"]
        name = author["name"]
        email = author["email"]
        license = author["license"]

        with open(subdir + "/files.yaml", 'r') as f:
            titles = yaml.full_load(f)

        for title in titles:
            proc_image(subdir, name, title, email, license, DEST, PREFIX)

if __name__ == "__main__":
    __main__()

# vim: set tabstop=4 expandtab :
