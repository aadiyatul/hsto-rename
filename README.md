# hsto-rename

A script for automatic replacement of image locations and formatting image tags in Markdown and HTML files.

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://www.gnu.org/licenses/gpl-3.0)

# Installation

```
pip install hsto-rename
```

will install the package globally. Alternatively, you can download the script `hsto-rename.py`.

# How to use

Call the package (or the script) with your local Python interpreter:

```
python -m hsto-rename input_file.md output_file.md
```

Without any extra arguments it will just copy the input file into the output one. 

## Converting image tags

To convert all the image links - both Markdown and HTML - to Markdown, use

```
python -m hsto-rename input_file.md output_file.md -f md
python -m hsto-rename input_file.md output_file.md --format=md
```

To convert all the links to HTML, use

```
python -m hsto-rename input_file.md output_file.md -f html
python -m hsto-rename input_file.md output_file.md --format=html
```

Use optional parameters to format the HTML images (they do not work in Markdown):

```
python -m hsto-rename input_file.md output_file.md -f html --width=600 --height=400 --align="center"
```

## Renaming the images

To automatically replace links to local images with the ones in the cloud, upload the images to the cloud and save all the links to the images into one file `cloud.txt`.

Then run
```
python -m hsto-rename input_file.md output_file.md -r cloud.txt
```

The script will find correspondence between local images and their copies in the cloud, and replace the links in the document.


