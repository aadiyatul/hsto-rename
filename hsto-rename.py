import os
import sys
import io
import requests
import re
from PIL import Image
from argparse import ArgumentParser


def find_tags(text: str, bare_urls=False):
    if bare_urls:
        return re.findall('https?:\/\/[^"\)\r\n]+',text)
    else:
        md_tags = re.findall('!\[.*\]\(.+\)',text)
        html_tags = re.findall('<img.*>',text)
        return md_tags + html_tags


class ImageTag():
    def __init__(self,tag: str, path='') -> None:
        self.tag = tag
        self.path = path
        self.type = ''
        self.link = None
        self._img = None
        self._img_failed = False
        self.width_tag = None
        self.height_tag = None
        self.align_tag = None
        self.alt_text = ''
        self._parse_tag()

    def __eq__(self, other: 'ImageTag') -> bool:
        if not self.type:
            return False
        if not self.img:
            return False
        return self.img == other.img
    
    @property
    def img(self):
        if self._img:
            return self._img
        if self._img_failed:
            return None
        self._load_img()
        return self.img

    def _parse_tag(self) -> None:
        if re.match('!\[.*\]\(.+\)',self.tag):
            # markdown tag
            self.type = 'md'
            # find the link
            prefix = re.match('!\[.*\]\(',self.tag)
            postfix = re.search('\s*"[^"]*"\s*\)',self.tag)
            if postfix:
                self.link = self.tag[prefix.end():postfix.start()].strip()
            else:
                self.link = self.tag[prefix.end():-1].strip()
            # find alt text
            self.alt_text = re.match('[^\]]*',self.tag[2:]).group(0)
        
        elif re.match('<img.*>',self.tag):
            # HTML tag
            self.type = 'html'
            # find the link
            s = re.search('src\s*=\s*"[^"]*"',self.tag)
            if not s:
                print(f'Cannot find "src" in "{self.tag}"')
                self.type = ''
            prefix = re.match('src\s*=\s*"',s.group(0))
            self.link = s.group(0)[prefix.end():-1].strip()
            # find alt text
            s = re.search('alt\s*=\s*"[^"]*"',self.tag)
            if s:
                prefix = re.match('alt\s*=\s*"',s.group(0))
                self.alt_text = s.group(0)[prefix.end():-1].strip()
            # find optional parameters
            s = re.search('width\s*=\s*"[^"]*"',self.tag)
            if s:
                self.width_tag = s.group(0)
            s = re.search('height\s*=\s*"[^"]*"',self.tag)
            if s:
                self.height_tag = s.group(0)
            s = re.search('align\s*=\s*"[^"]*"',self.tag)
            if s:
                self.align_tag = s.group(0)
        
        elif re.match('https?:\/\/',self.tag):
            # bare URL
            self.type = 'url'
            self.link = self.tag

        else:
            print(f'Tag "{self.tag}" is not recognized')

    def _load_img(self):
        try:
            if os.path.isfile(os.path.join(self.path,self.link)):
                self._img = Image.open(os.path.join(self.path,self.link))
            else:
                response = requests.get(self.link)
                image_bytes = io.BytesIO(response.content)
                self._img = Image.open(image_bytes)
        except:
            self._img_failed = True
            print(f'Cannot access image "{self.link}"')

    def to_html(self, width=None, height=None, align=None) -> None:
        if self.type == 'md':
            new_tag = '<img src="' + self.link + '"'
            if self.alt_text:
                new_tag += f' alt="{self.alt_text}"'
            if width:
                new_tag += f' width="{width}"'
            if height:
                new_tag += f' height="{height}"'
            if align:
                new_tag += f' align="{align}"'
            new_tag += ">"
            return new_tag

        elif self.type == 'html':
            new_tag = self.tag
            if width:
                if self.width_tag:
                    new_tag = new_tag.replace(self.width_tag,f'width="{width}"')
                else:
                    new_tag = new_tag[:-1] + f' width="{width}"' + ">"
            if height:
                if self.height_tag:
                    new_tag = new_tag.replace(self.height_tag,f'height="{height}"')
                else:
                    new_tag = new_tag[:-1] + f' height="{height}"' + ">"
            if align:
                if self.align_tag:
                    new_tag = new_tag.replace(self.align_tag,f'align="{align}"')
                else:
                    new_tag = new_tag[:-1] + f' align="{align}"' + ">"
            return new_tag
        
        else:
            print(f'Tag "{self.tag}" is ill-defiened, cannot convert')
            return None

    def to_markdown(self) -> None:
        if self.type == 'md':
            return self.tag
        
        elif self.type == 'html':
            return '![' + self.alt_text + '](' + self.link + ')'

        else:
            print(f'Tag "{self.tag}" is ill-defiened, cannot convert')
            return None      


def main(file_in,file_out,format=None,rename=None,
        width=None,height=None,align=None):
    if not os.path.isfile(file_in):
        raise ValueError(f'Cannot find the file "{file_in}"')

    dir_in = os.path.dirname(file_in)
    with open(file_in,'r',encoding="UTF-8") as f:
        text = f.read()
    tags = find_tags(text)
    text_tags = [ImageTag(tag,path=dir_in) for tag in tags]

    if format:
        if format == 'md':
            if width or height or align:
                print(f'Width, height, and alignment can only be defined when converting to HTML tags')
            
            for tag in text_tags:
                new_tag = tag.to_markdown()
                text = text.replace(tag.tag, new_tag)

        elif format == 'html':
            for tag in text_tags:
                new_tag = tag.to_html(width=width,height=height,align=align)
                text = text.replace(tag.tag, new_tag)
    
    if rename:
        if not os.path.isfile(rename):
            raise ValueError(f'Cannot find the file "{rename}"')

        with open(rename,'r') as f:
            content = f.read()
        hsto_urls = find_tags(content,bare_urls=True)
        hsto_tags = [ImageTag(url) for url in hsto_urls]

        for tag in text_tags:
            matched = False
            for hsto_tag in hsto_tags:
                if hsto_tag == tag:
                    text = text.replace(tag.link,hsto_tag.link)
                    matched = True
                    break
            if not matched:
                print(f'No matching image found for "{tag.link}"')

    with open(file_out,'w',encoding="UTF-8") as f:
        f.write(text)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("file_in", type=str,
                        help="Input file to be processed")
    parser.add_argument("file_out", type=str,
                        help="Processed file")
    parser.add_argument("-f", "--format", type=str, choices=['md','html'],
                        help="Format of image tags in the output file")
    parser.add_argument("-r", "--rename", type=str,
                        help="File with external image links")
    parser.add_argument("--width", type=str,
                        help="Width of figures (only for HTML tags)")
    parser.add_argument("--height", type=str,
                        help="Height of figures (only for HTML tags)")
    parser.add_argument("--align", type=str,
                        help="Alignment of figures (only for HTML tags)")
    args = parser.parse_args()

    if not os.path.isfile(args.file_in):
        print(f'Cannot find the file "{args.file_in}"')
        sys.exit(1)

    if args.rename and not os.path.isfile(args.rename):
        print(f'Cannot find the file "{args.rename}"')
        sys.exit(1)
    
    main(args.file_in,args.file_out,format=args.format,rename=args.rename,
        width=args.width,height=args.height,align=args.align)
