#!/bin/python3

import argparse
import sys
import shutil
import os
import os.path
import yaml

CWD = os.getcwd()

IMG_DIR = "/usr/share/backgrounds"
IMG_PATH = IMG_DIR + "/%s.jpg"
XML_DIR = "/usr/share/background-properties"
XML_PATH = XML_DIR + "/%s.xml"

GNOME_XML_DIR = "/usr/share/gnome-background-properties"
GNOME_XML_PATH = GNOME_XML_DIR + "/%s.xml"

MATE_XML_DIR = "/usr/share/gnome-background-properties"
MATE_XML_PATH = MATE_XML_DIR + "/%s.xml"

XFCE_IMG_DIR = "/usr/share/backgrounds/xfce"
XFCE_IMG_PATH = XFCE_IMG_DIR + "/%s.jpg"

KDE_PATH = "/usr/share/wallpapers/%s"
KDE_IMG_PATH = KDE_PATH + "/contents/images/%s.jpg"

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


def proc_image(subdir, author, title, email, license, prefix):
    print("Author: %s, Image: %s" % (author, title))
    fname = normalize_fname(title)

    # Path to solid output xml, not symlink
    xml_path = XML_PATH % fname
    img_path = IMG_PATH % fname

    # Path to symlinks
    gnome_xml_path = GNOME_XML_PATH % fname
    mate_xml_path = MATE_XML_PATH % fname
    xfce_img_path = XFCE_IMG_PATH % fname
    kde_path = KDE_PATH % fname
    kde_img_path = KDE_IMG_PATH % (fname, fname)

    # Meta data content
    xml_content = XML_IN.replace("%TITLE%", title).replace("%FILENAME%", img_path)
    desktop_content = DESKTOP_IN.replace("%TITLE%", title) \
            .replace("%AUTHOR%", author) \
            .replace("%EMAIL%", email) \
            .replace("%LICENSE%", license)

    # Install directories
    mkdir(prefix + kde_path + "/contents/images")

    # Install base images, xmls
    src_img = subdir + "/" + fname + ".jpg"
    copy(src_img, prefix + img_path);
    with open(prefix + xml_path, "w") as f:
        f.write(xml_content)

    # Create XML links for Gnome and Mate
    ln(prefix + gnome_xml_path, xml_path)
    ln(prefix + mate_xml_path, xml_path)

    # Handle KDE
    # Install desktop file and data structure
    with open(prefix + kde_path + "/metadata.desktop", "w") as f:
        f.write(desktop_content)
    mkdir(prefix + kde_path + "/contents/images")
    ln(prefix + kde_img_path, img_path)


def __main__():
    parser = argparse.ArgumentParser(description='Generate data')
    parser.add_argument('--output', default=".", help="Output dir")
    arg = parser.parse_args()

    PREFIX = arg.output

    with open(AUTHORS, 'r') as f:
        authors = yaml.load(f)

    mkdir(PREFIX + IMG_DIR)
    mkdir(PREFIX + XML_DIR)
    mkdir(PREFIX + GNOME_XML_DIR)
    mkdir(PREFIX + MATE_XML_DIR)
    mkdir(PREFIX + XFCE_IMG_DIR)

    for author in authors:
        subdir = CWD + "/" + author["dir"]
        name = author["name"]
        email = author["email"]
        license = author["license"]

        with open(subdir + "/files.yaml", 'r') as f:
            titles = yaml.load(f)

        for title in titles:
            proc_image(subdir, name, title, email, license, PREFIX)

if __name__ == "__main__":
    __main__()

# vim: set tabstop=4 expandtab :
