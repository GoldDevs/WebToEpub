import unittest
import zipfile
import tempfile
import os
from src.web_to_epub.epub_generator import EpubGenerator

class TestEpubGenerator(unittest.TestCase):

    def test_advanced_settings(self):
        # 1. Create an EpubGenerator with advanced settings
        gen = EpubGenerator(
            title="Test Book",
            author="Test Author",
            epub3=True,
            series_name="Test Series",
            series_index="1",
            custom_stylesheet="body { color: red; }"
        )

        # 2. Add a chapter
        gen.add_chapter("Chapter 1", "<h1>Chapter 1</h1><p>Content</p>", 1)

        # 3. Save the book to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
            tmp_path = tmp.name

        gen.save(tmp_path)

        # 4. Read the saved EPUB and check its contents
        with zipfile.ZipFile(tmp_path, 'r') as zf:
            # Determine the root directory (OEBPS for EPUB2, EPUB for EPUB3)
            namelist = zf.namelist()
            root_dir = "EPUB" if "EPUB/content.opf" in namelist else "OEBPS"

            # Check for stylesheet
            css_path = f'{root_dir}/style/main.css'
            self.assertIn(css_path, namelist)
            css_content = zf.read(css_path).decode('utf-8')
            self.assertEqual(css_content, "body { color: red; }")

            # Check OPF file for EPUB version and series metadata
            opf_path = f'{root_dir}/content.opf'
            self.assertIn(opf_path, namelist)
            opf_content = zf.read(opf_path).decode('utf-8')

            self.assertIn('version="3.0"', opf_content)

            # Parse the OPF content as XML and check for metadata
            import xml.etree.ElementTree as ET
            root = ET.fromstring(opf_content)

            # Find series and series_index tags, ignoring the namespace prefix
            series_found = False
            series_index_found = False
            for elem in root.iter():
                if elem.tag.endswith('series') and elem.text == 'Test Series':
                    series_found = True
                if elem.tag.endswith('series_index') and elem.text == '1':
                    series_index_found = True

            self.assertTrue(series_found, "Series metadata not found")
            self.assertTrue(series_index_found, "Series index metadata not found")

        # Clean up the temporary file
        os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
