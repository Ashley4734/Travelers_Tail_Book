#!/usr/bin/env python3
"""
Create an EPUB file for "The Traveler's Key" by Ashley Harris
"""

import os
import re
import zipfile
from pathlib import Path
from datetime import datetime
import html

class EPUBCreator:
    def __init__(self, book_file, front_matter_file, back_matter_file, output_dir="epub_output"):
        self.book_file = book_file
        self.front_matter_file = front_matter_file
        self.back_matter_file = back_matter_file
        self.output_dir = Path(output_dir)
        self.chapters = []

    def read_file(self, filename):
        """Read a file and return its contents"""
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_chapters(self):
        """Extract chapters from the book file"""
        content = self.read_file(self.book_file)

        # Split by chapter markers
        chapter_pattern = r'(Chapter \d+:?[^\n]*)'
        parts = re.split(chapter_pattern, content)

        # The first part is the front matter in the book file (before Chapter 1)
        # We'll skip it since we have a separate front matter file

        current_chapter = None
        for i, part in enumerate(parts):
            if re.match(r'Chapter \d+', part):
                current_chapter = part.strip()
            elif current_chapter and part.strip():
                # Clean up the chapter text
                chapter_text = part.strip()
                self.chapters.append({
                    'title': current_chapter,
                    'content': chapter_text
                })
                current_chapter = None

        print(f"Extracted {len(self.chapters)} chapters")
        return self.chapters

    def create_directory_structure(self):
        """Create the EPUB directory structure"""
        # Create main directory
        self.output_dir.mkdir(exist_ok=True)

        # Create required directories
        (self.output_dir / "META-INF").mkdir(exist_ok=True)
        (self.output_dir / "OEBPS").mkdir(exist_ok=True)
        (self.output_dir / "OEBPS" / "Text").mkdir(exist_ok=True)
        (self.output_dir / "OEBPS" / "Styles").mkdir(exist_ok=True)

        print(f"Created EPUB directory structure at {self.output_dir}")

    def create_mimetype(self):
        """Create the mimetype file"""
        with open(self.output_dir / "mimetype", 'w', encoding='utf-8') as f:
            f.write("application/epub+zip")

    def create_container_xml(self):
        """Create META-INF/container.xml"""
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''

        with open(self.output_dir / "META-INF" / "container.xml", 'w', encoding='utf-8') as f:
            f.write(container_xml)

    def create_css(self):
        """Create the CSS stylesheet"""
        css = '''@charset "UTF-8";

body {
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
    margin: 1em;
    text-align: justify;
}

h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
    text-align: center;
    margin: 2em 0 1em 0;
    page-break-after: avoid;
}

h1 {
    font-size: 2em;
    font-weight: bold;
    margin-top: 3em;
}

h2 {
    font-size: 1.5em;
    font-weight: bold;
}

h3 {
    font-size: 1.2em;
    font-style: italic;
}

p {
    margin: 0;
    text-indent: 1.5em;
}

p.first, p.no-indent {
    text-indent: 0;
}

.copyright, .dedication, .acknowledgments {
    text-align: center;
    margin: 2em 0;
    text-indent: 0;
}

.title-page {
    text-align: center;
    margin-top: 3em;
}

.title {
    font-size: 2.5em;
    font-weight: bold;
    margin: 2em 0;
}

.author {
    font-size: 1.5em;
    margin: 2em 0;
}

.separator {
    text-align: center;
    margin: 2em 0;
    font-size: 1.5em;
}

.chapter-title {
    text-align: center;
    font-size: 1.8em;
    font-weight: bold;
    margin: 3em 0 2em 0;
    page-break-before: always;
}

.front-matter, .back-matter {
    margin: 2em 0;
}

.front-matter p, .back-matter p {
    text-indent: 0;
    margin-bottom: 1em;
}

.blurb {
    text-align: left;
    margin: 1em 2em;
}

.praise {
    font-style: italic;
    text-align: center;
    margin: 1em 2em;
}'''

        with open(self.output_dir / "OEBPS" / "Styles" / "style.css", 'w', encoding='utf-8') as f:
            f.write(css)

    def escape_html(self, text):
        """Escape HTML special characters"""
        return html.escape(text)

    def format_paragraph(self, text, is_first=False):
        """Format a paragraph with proper HTML"""
        text = self.escape_html(text.strip())
        class_attr = ' class="first"' if is_first else ''
        return f'    <p{class_attr}>{text}</p>\n'

    def create_title_page(self):
        """Create the title page"""
        html_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>The Traveler's Key</title>
    <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
</head>
<body>
    <div class="title-page">
        <h1 class="title">THE TRAVELER'S KEY</h1>
        <p class="author">A Novel by<br/>ASHLEY HARRIS</p>
    </div>
</body>
</html>'''

        with open(self.output_dir / "OEBPS" / "Text" / "title.xhtml", 'w', encoding='utf-8') as f:
            f.write(html_content)

    def create_copyright_page(self):
        """Create the copyright page"""
        front_matter = self.read_file(self.front_matter_file)

        html_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>Copyright</title>
    <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
</head>
<body>
    <div class="front-matter">
        <div class="copyright">
            <p class="no-indent"><strong>Copyright © 2025 by Ashley Harris</strong></p>
            <p class="no-indent">All rights reserved.</p>
            <br/>
            <p class="no-indent">No part of this book may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the prior written permission of the author.</p>
            <br/>
            <p class="no-indent">This is a work of fiction. Names, characters, places, and incidents are either the product of the author's imagination or are used fictitiously. Any resemblance to actual persons, living or dead, events, or locales is entirely coincidental.</p>
            <br/>
            <p class="no-indent"><strong>First Edition</strong></p>
            <br/>
            <p class="no-indent">ISBN: [To be assigned]</p>
            <p class="no-indent">Cover design by [To be assigned]</p>
        </div>

        <div class="dedication">
            <h2>Dedication</h2>
            <p class="no-indent">For everyone who has ever stared at the ceiling<br/>
            and wondered if there's more to life than this.</p>
            <br/>
            <p class="no-indent">For the dreamers who never stopped dreaming.</p>
            <br/>
            <p class="no-indent">For those who found magic in ordinary moments.</p>
        </div>

        <div class="acknowledgments">
            <h2>Acknowledgments</h2>
            <p class="no-indent">To the readers who believe in the extraordinary hiding within the ordinary—thank you for taking this journey.</p>
            <br/>
            <p class="no-indent">To every person who has ever felt stuck in the monotony of daily life and dreamed of adventure—this story is for you.</p>
            <br/>
            <p class="no-indent">And to Mayfield, Iowa, and all the small towns like it—where every dreamer's journey begins.</p>
        </div>
    </div>
</body>
</html>'''

        with open(self.output_dir / "OEBPS" / "Text" / "copyright.xhtml", 'w', encoding='utf-8') as f:
            f.write(html_content)

    def create_chapter_file(self, chapter_num, chapter_title, chapter_content):
        """Create an XHTML file for a chapter"""
        # Split content into paragraphs
        paragraphs = [p.strip() for p in chapter_content.split('\n') if p.strip()]

        html_content = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{self.escape_html(chapter_title)}</title>
    <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
</head>
<body>
    <h1 class="chapter-title">{self.escape_html(chapter_title)}</h1>
'''

        # Add paragraphs
        for i, para in enumerate(paragraphs):
            is_first = (i == 0)
            html_content += self.format_paragraph(para, is_first)

        html_content += '''</body>
</html>'''

        filename = f"chapter_{chapter_num:02d}.xhtml"
        with open(self.output_dir / "OEBPS" / "Text" / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename

    def create_back_matter(self):
        """Create the back matter (about the author, etc.)"""
        back_matter = self.read_file(self.back_matter_file)

        html_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>About the Book</title>
    <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
</head>
<body>
    <div class="back-matter">
        <h2>About The Traveler's Key</h2>
        <div class="blurb">
            <p class="no-indent">Jeff Thorne's life in Mayfield, Iowa is the definition of ordinary. Same job. Same routine. Same crushing sense that there should be more to existence than this.</p>
            <br/>
            <p class="no-indent">Then he finds a book at a yard sale.</p>
            <br/>
            <p class="no-indent">No title. No author. Just strange symbols and impossible drawings of worlds beyond imagination. When Jeff follows the book's cryptic instructions to an old bridge in Mayfield Park, he discovers a portal to the Nexus Market—a crossroads where countless realities converge, where beings from across the multiverse trade in wonders and impossibilities.</p>
            <br/>
            <p class="no-indent">The book chose him. Now Jeff is a Traveler.</p>
            <br/>
            <p class="no-indent">But the gift of crossing worlds comes with a price. Reality itself is fraying at the edges, and an ancient force known as the Void seeks to unmake everything that exists. As Jeff joins the Guardian Conclave—a band of protectors from across the infinite realms—he must learn to wield the Codex's power before the balance of existence collapses.</p>
            <br/>
            <p class="no-indent">From the mundane streets of a small Midwestern town to the furthest reaches of the cosmic tapestry, Jeff Thorne will discover that the extraordinary has always been hiding in plain sight. That every reality, no matter how small, matters. And that sometimes the most ordinary person can become the key to saving everything.</p>
            <br/>
            <p class="no-indent"><em>Perfect for fans of portal fantasy, multiverse adventures, and stories where the everyday becomes extraordinary.</em></p>
        </div>

        <h2>About the Author</h2>
        <p class="no-indent" style="text-align: center;">Ashley Harris is a storyteller fascinated by the extraordinary potential hidden within ordinary lives. THE TRAVELER'S KEY is their debut novel, exploring themes of belonging, purpose, and the infinite possibilities that exist just beyond the veil of our everyday reality.</p>
    </div>
</body>
</html>'''

        with open(self.output_dir / "OEBPS" / "Text" / "about.xhtml", 'w', encoding='utf-8') as f:
            f.write(html_content)

    def create_content_opf(self, chapter_files):
        """Create the content.opf file"""
        # Generate manifest items for chapters
        manifest_items = ''
        spine_items = ''

        # Add fixed items
        manifest_items += '    <item id="title" href="Text/title.xhtml" media-type="application/xhtml+xml"/>\n'
        manifest_items += '    <item id="copyright" href="Text/copyright.xhtml" media-type="application/xhtml+xml"/>\n'

        spine_items += '    <itemref idref="title"/>\n'
        spine_items += '    <itemref idref="copyright"/>\n'

        # Add chapters
        for i, filename in enumerate(chapter_files, 1):
            item_id = f"chapter_{i:02d}"
            manifest_items += f'    <item id="{item_id}" href="Text/{filename}" media-type="application/xhtml+xml"/>\n'
            spine_items += f'    <itemref idref="{item_id}"/>\n'

        # Add back matter
        manifest_items += '    <item id="about" href="Text/about.xhtml" media-type="application/xhtml+xml"/>\n'
        spine_items += '    <itemref idref="about"/>\n'

        # Add CSS
        manifest_items += '    <item id="style" href="Styles/style.css" media-type="text/css"/>\n'

        # Add NCX
        manifest_items += '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'

        content_opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>The Traveler's Key</dc:title>
    <dc:creator opf:role="aut">Ashley Harris</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">urn:uuid:travelers-key-2025</dc:identifier>
    <dc:publisher>Ashley Harris</dc:publisher>
    <dc:date>{datetime.now().year}</dc:date>
    <dc:subject>Fantasy</dc:subject>
    <dc:subject>Portal Fantasy</dc:subject>
    <dc:subject>Multiverse</dc:subject>
    <dc:subject>Adventure</dc:subject>
    <dc:description>Jeff Thorne discovers a mysterious book that leads him to the Nexus Market, a crossroads between realities. As a newly chosen Traveler, he must learn to wield the power of the Codex and join the Guardian Conclave to protect existence itself from the encroaching Void.</dc:description>
    <dc:rights>Copyright © 2025 by Ashley Harris. All rights reserved.</dc:rights>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
{manifest_items}  </manifest>
  <spine toc="ncx">
{spine_items}  </spine>
  <guide>
    <reference type="title-page" title="Title Page" href="Text/title.xhtml"/>
    <reference type="copyright-page" title="Copyright" href="Text/copyright.xhtml"/>
    <reference type="text" title="Beginning" href="Text/chapter_01.xhtml"/>
  </guide>
</package>'''

        with open(self.output_dir / "OEBPS" / "content.opf", 'w', encoding='utf-8') as f:
            f.write(content_opf)

    def create_toc_ncx(self):
        """Create the toc.ncx navigation file"""
        nav_points = ''
        play_order = 1

        # Title page
        nav_points += f'''    <navPoint id="navpoint-{play_order}" playOrder="{play_order}">
      <navLabel>
        <text>Title Page</text>
      </navLabel>
      <content src="Text/title.xhtml"/>
    </navPoint>
'''
        play_order += 1

        # Copyright
        nav_points += f'''    <navPoint id="navpoint-{play_order}" playOrder="{play_order}">
      <navLabel>
        <text>Copyright</text>
      </navLabel>
      <content src="Text/copyright.xhtml"/>
    </navPoint>
'''
        play_order += 1

        # Chapters
        for i, chapter in enumerate(self.chapters, 1):
            nav_points += f'''    <navPoint id="navpoint-{play_order}" playOrder="{play_order}">
      <navLabel>
        <text>{self.escape_html(chapter['title'])}</text>
      </navLabel>
      <content src="Text/chapter_{i:02d}.xhtml"/>
    </navPoint>
'''
            play_order += 1

        # About
        nav_points += f'''    <navPoint id="navpoint-{play_order}" playOrder="{play_order}">
      <navLabel>
        <text>About the Book</text>
      </navLabel>
      <content src="Text/about.xhtml"/>
    </navPoint>
'''

        toc_ncx = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:travelers-key-2025"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>The Traveler's Key</text>
  </docTitle>
  <docAuthor>
    <text>Ashley Harris</text>
  </docAuthor>
  <navMap>
{nav_points}  </navMap>
</ncx>'''

        with open(self.output_dir / "OEBPS" / "toc.ncx", 'w', encoding='utf-8') as f:
            f.write(toc_ncx)

    def create_epub(self, output_filename="The_Travelers_Key.epub"):
        """Package everything into an EPUB file"""
        epub_path = Path(output_filename)

        # Create ZIP file (EPUB is a ZIP with specific structure)
        with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            # Add mimetype first (must be uncompressed and first in archive)
            epub.write(self.output_dir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)

            # Add META-INF
            epub.write(self.output_dir / "META-INF" / "container.xml", "META-INF/container.xml")

            # Add all OEBPS files
            for root, dirs, files in os.walk(self.output_dir / "OEBPS"):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_dir)
                    epub.write(file_path, arcname)

        print(f"\nEPUB created successfully: {epub_path}")
        print(f"File size: {epub_path.stat().st_size / 1024:.2f} KB")
        return epub_path

    def build(self):
        """Build the complete EPUB"""
        print("Starting EPUB creation for 'The Traveler's Key'")
        print("=" * 60)

        # Extract chapters
        print("\n1. Extracting chapters...")
        self.extract_chapters()

        # Create directory structure
        print("\n2. Creating directory structure...")
        self.create_directory_structure()

        # Create mimetype
        print("\n3. Creating mimetype...")
        self.create_mimetype()

        # Create container.xml
        print("\n4. Creating container.xml...")
        self.create_container_xml()

        # Create CSS
        print("\n5. Creating stylesheet...")
        self.create_css()

        # Create title page
        print("\n6. Creating title page...")
        self.create_title_page()

        # Create copyright page
        print("\n7. Creating copyright page...")
        self.create_copyright_page()

        # Create chapter files
        print("\n8. Creating chapter files...")
        chapter_files = []
        for i, chapter in enumerate(self.chapters, 1):
            filename = self.create_chapter_file(i, chapter['title'], chapter['content'])
            chapter_files.append(filename)
            print(f"   Created: {chapter['title']}")

        # Create back matter
        print("\n9. Creating back matter...")
        self.create_back_matter()

        # Create content.opf
        print("\n10. Creating content.opf...")
        self.create_content_opf(chapter_files)

        # Create toc.ncx
        print("\n11. Creating table of contents...")
        self.create_toc_ncx()

        # Package EPUB
        print("\n12. Packaging EPUB file...")
        epub_file = self.create_epub()

        print("\n" + "=" * 60)
        print("EPUB creation complete!")
        print("=" * 60)

        return epub_file


def main():
    """Main function"""
    creator = EPUBCreator(
        book_file="THE_TRAVELERS_KEY_FINAL.txt",
        front_matter_file="FRONT_MATTER.txt",
        back_matter_file="BACK_COVER_BLURB.txt"
    )

    epub_file = creator.build()
    print(f"\nYour EPUB is ready: {epub_file}")
    print("\nYou can now read this file on any e-reader device or app that supports EPUB format.")


if __name__ == "__main__":
    main()
