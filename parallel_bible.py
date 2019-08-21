from pysword.modules import SwordModules
import uuid
import os
import sys
import pyphen
import shutil

class ParallelBible:

    translations = { "la": { "bible": "Biblia",
                             "book": "Liber",
                             "chapter": "Caput" },
                     "en": { "bible": "Bible",
                             "book": "Book",
                             "chapter": "Chapter" },
                     "ru": { "bible": "Библия",
                             "book": "Книга",
                             "chapter": "Глава" }
    }

    rtl_bibles = ["HebModern", "WLC"]

    def __init__(self, left, right, modules_dir="Modules/", hyphen_lang="en_GB"):
        self.left = left
        self.right = right
        modules = SwordModules(modules_dir + left + '.zip')
        found_modules = modules.parse_modules()
        self.bible1 = modules.get_bible_from_module(left)
        self.books1 = self.bible1.get_structure().get_books()
        self.books1 = self.books1.get('ot', []) + self.books1.get('nt', [])
        
        modules = SwordModules(modules_dir + right + '.zip')
        found_modules = modules.parse_modules()
        self.bible2 = modules.get_bible_from_module(right)
        self.books2 = self.bible2.get_structure().get_books()
        self.books2 = self.books2['ot'] + self.books2['nt']

        self.uuid = str(uuid.uuid4())
        self.hyphenator2 = pyphen.Pyphen(lang=hyphen_lang)

    def generate(self, books=None, chapters=None, verses=None, trans1="en", trans2=None):
        z = 1
        results = {}
        toc = ""
        nav = ""
        left_rtl = "dir=\"rtl\"" if self.left in self.rtl_bibles else ""
        right_rtl = "dir=\"rtl\"" if self.right in self.rtl_bibles else ""
        bible_heading = self.left + " || " + self.right
        nav += """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
        "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta http-equiv="Content-Style-Type" content="text/css"/>
        <meta name="generator" content="pandoc"/>
        <title>{0}</title>
        <style>
        ol { list-style-type: none; margin: 0; padding: 0; }
        .toc-chapter {
        display: inline
        }
        </style>
        </head>
        <body>
        <nav role="doc-toc" type="toc" id="toc">
        <h2>Table of Contents</h2>
        <ol>
        """
        toc += """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
        "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
        <meta name="dtb:uid" content="urn:uuid:{2}"/>
        <meta name="dtb:depth" content="{0}"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
        </head>
        <docTitle>
        <text>{1}</text>
        </docTitle>
        <navMap>
        """.format(2, bible_heading, self.uuid)

        for (i, book1) in enumerate(self.books1):
            if books is not None and i not in books:
                continue
            print("Processing book {0}".format(book1.name))
            try:
                _, book2 = self.bible2.get_structure().find_book(book1.name)
            except ValueError:
                print("Book {0} not found in {1}".format(book1.name, self.right))
                continue

            book_heading = book1.name

            res = """<?xml version="1.0" encoding="utf-8"?>
                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
                    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

                    <html xmlns="http://www.w3.org/1999/xhtml">
                    <head>
                    <title>{0}</title>
                    <style>
                    body {{ word-wrap: break-all; 
                    -epub-hyphens: auto;
                    -webkit-hyphens: auto;
                    -ms-hyphens: auto;
                    hyphens: auto;
                    adobe-hyphenate: auto;
                    }}
                    .toc_subheading {{
                    display: inline
                    }}
                    table {{
                    border-collapse: collapse;
                    }}
                    table, th, td {{
                    border: none;  
                    }}  
                    h1, h2 {{ text-align: center; }}
                    sup {{ color: red }}
                    .td_r {{ font-size: 75%  }}
                    </style>
                    </head>
                    <body>
                    <h1>{0}</h1>\n
                    """.format(book_heading)

            toc += """<navPoint id="navPoint-{0}" playOrder="{0}">
            <navLabel>
            <text>{1}</text>
            </navLabel>
            <content src="Text/{1}.xhtml"/>
            </navPoint>
            """.format(str(z), book_heading)
            nav += """<li><span>{0}</span>
            <ol>
            """.format(book_heading)
            #z += 1
            for (ch_i, ch_len) in enumerate(book1.chapter_lengths):
                ch_i += 1
                if chapters is not None and (i, ch_i) not in chapters:
                    continue
                chapter_heading = self.translations[trans1]["chapter"] + " " + str(ch_i)
                print("|", end="", flush=True)
                if trans2:
                    chapter_heading += " | " + self.translations[trans2]["chapter"] + " " + str(ch_i)
            
                res += "<h2 id=\"toc_{0}\">{1}</h2>\n".format(str(z), chapter_heading)

                for verse_i in range(ch_len):
                    res += "<table>\n"
                    verse_i += 1
                    if verses is not None and verse_i not in verses:
                        continue
                    verse1 = self.bible1.get(books=book1.name, chapters=ch_i, verses=verse_i)

                    try:
                        verse2 = self.bible2.get(books=book2.name, chapters=ch_i, verses=verse_i)
                    except ValueError as e:
                        verse2 = "-//-"

                    #verse1 = "\xad".join(list(verse1))
                    verse2 = " ".join(map(lambda w: self.hyphenator2.inserted(w, hyphen='&shy;\xad'), verse2.split()))
                    
                    res += """<tr>
                    <td {3} valign=\"top\">\n<sup>{0} </sup>{1}</td>\n
                    <td {4} valign=\"top\" class="td_r"><sup>{0} </sup>{2}</td>\n
                    </tr>\n\n""".format(str(ch_i) + ":" + str(verse_i), verse1, verse2, left_rtl, right_rtl)
                    res += "</table>\n"
                toc += """<navPoint class="toc_subheading" id="navPoint-{0}" playOrder="{0}">
                <navLabel>
                <text>{1}&nbsp</text>
                </navLabel>
                <content src="Text/{2}.xhtml#toc_{0}"/>
                </navPoint>
                """.format(str(z), chapter_heading, book_heading)
                nav += """<li class="toc-chapter">
                <a href="../Text/{2}.xhtml#toc_{0}">{1}</a>
                </li>
                """.format(str(z), str(ch_i), book_heading)
                z += 1
            nav += """</ol></li>
            """
            print()
            res += """
            </body>
            </html>
            """
            results[book_heading] = res
        toc += """
        </navMap>
        </ncx>
        """
        nav += """</ol>
        </nav>
        </body>
        </html>
        """
        content = """<?xml version="1.0" encoding="utf-8"?>
        <package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:{0}</dc:identifier>
        <dc:language>{2}</dc:language>
        <dc:title>{1}</dc:title>
        <meta content="0.9.9" name="Sigil version" />
        <dc:date xmlns:opf="http://www.idpf.org/2007/opf" opf:event="modification">2019-07-30</dc:date>
        </metadata>
        <manifest>
        <item id="nav" href="Text/nav.xhtml" media-type="application/xhtml+xml"/>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        """.format(self.uuid, bible_heading, trans1)
        for book_heading in results:
            content += '<item id="{0}.xhtml" href="Text/{0}.xhtml" media-type="application/xhtml+xml"/>\n'.format(book_heading)
        content += """</manifest>
        <spine toc="ncx">"""
        for book_heading in results:
            content += '<itemref idref="{0}.xhtml" />'.format(book_heading)
        content += """</spine>
        <guide>
        <reference type="toc" title="{1}" href="Text/nav.xhtml"/>
        </guide>
        </package>
        """.format(self.uuid, bible_heading, trans1)
        
        return results, toc, content, nav

    def save_epub(self, name, path, res_path="res/", books=None, chapters=None, verses=None, trans1="en", trans2=None, mk_mobi=True):
        os.makedirs(path, exist_ok=True)
        os.makedirs(path + "Text/", exist_ok=True)
        books, toc, content, nav = self.generate(trans1=trans1, trans2=trans2, books=books, chapters=chapters, verses=verses)
        for book_heading in books:
            with open(path + "Text/" + book_heading + ".xhtml", "w+") as f:
                f.write(books[book_heading])
        with open(path + "toc.ncx", "w+") as f:
            f.write(toc)
        with open(path + "content.opf", "w+") as f:
            f.write(content)
        with open(path + "Text/nav.xhtml", "w+") as f:
            f.write(nav)
        
        shutil.make_archive(res_path + name, 'zip', path)
        shutil.rmtree(path)
        os.rename(res_path + name + ".zip", res_path + name + ".epub")
        if mk_mobi:
            os.system("ebook-convert {0} {1} --disable-dehyphenate".format(res_path + name + ".epub", res_path + name + ".mobi"))

