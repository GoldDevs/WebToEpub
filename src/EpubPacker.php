<?php

namespace App;

use ZipArchive;
use DOMDocument;

class EpubPacker
{
    private string $title;
    private string $author;
    private array $chapters; // e.g., [['title' => 'Chapter 1', 'content' => DOMDocument]]
    private string $uuid;

    /**
     * @param string $title
     * @param string $author
     * @param array $chapters Array of chapters, each an associative array with 'title' and 'content' (as DOMDocument)
     */
    public function __construct(string $title, string $author, array $chapters)
    {
        $this->title = $title;
        $this->author = $author;
        $this->chapters = $chapters;
        $this->uuid = 'urn:uuid:' . uniqid();
    }

    public function createEpub(): string
    {
        $zip = new ZipArchive();
        $filename = tempnam(sys_get_temp_dir(), 'epub_');
        if ($zip->open($filename, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== TRUE) {
            throw new \Exception("Cannot create epub file at $filename");
        }

        // Add mimetype file, must be first and uncompressed
        $zip->addFromString('mimetype', 'application/epub+zip');
        $zip->setCompressionName('mimetype', ZipArchive::CM_STORE);

        // Add container.xml
        $zip->addFromString('META-INF/container.xml', $this->getContainerXml());

        // Add content.opf
        $zip->addFromString('OEBPS/content.opf', $this->getContentOpf());

        // Add toc.ncx
        $zip->addFromString('OEBPS/toc.ncx', $this->getTocNcx());

        // Add stylesheet
        $zip->addFromString('OEBPS/style.css', $this->getStylesheet());

        // Add chapters
        foreach ($this->chapters as $index => $chapter) {
            $chapterFilename = 'OEBPS/Text/chapter' . ($index + 1) . '.xhtml';
            $chapterContent = $chapter['content'] instanceof DOMDocument ? $chapter['content']->saveHTML() : $chapter['content'];
            $zip->addFromString($chapterFilename, $this->getChapterXhtml($chapter['title'], $chapterContent));
        }

        $zip->close();

        return $filename;
    }

    private function getContainerXml(): string
    {
        return <<<XML
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
XML;
    }

    private function getStylesheet(): string
    {
        return "/* A default stylesheet */\nbody { margin: 5px; }";
    }

    private function getChapterXhtml(string $title, string $content): string
    {
        return <<<XHTML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>$title</title>
  <link rel="stylesheet" type="text/css" href="../style.css" />
</head>
<body>
  <h1>$title</h1>
  $content
</body>
</html>
XHTML;
    }

    private function getContentOpf(): string
    {
        $doc = new DOMDocument('1.0', 'UTF-8');
        $doc->formatOutput = true;

        $package = $doc->createElement('package');
        $package->setAttribute('xmlns', 'http://www.idpf.org/2007/opf');
        $package->setAttribute('unique-identifier', 'BookId');
        $package->setAttribute('version', '2.0');
        $doc->appendChild($package);

        // Metadata
        $metadata = $doc->createElement('metadata');
        $metadata->setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/');
        $metadata->setAttribute('xmlns:opf', 'http://www.idpf.org/2007/opf');
        $package->appendChild($metadata);

        $dcTitle = $doc->createElement('dc:title', $this->title);
        $metadata->appendChild($dcTitle);

        $dcCreator = $doc->createElement('dc:creator', $this->author);
        $dcCreator->setAttribute('opf:role', 'aut');
        $metadata->appendChild($dcCreator);

        $dcIdentifier = $doc->createElement('dc:identifier', $this->uuid);
        $dcIdentifier->setAttribute('id', 'BookId');
        $metadata->appendChild($dcIdentifier);

        $dcLanguage = $doc->createElement('dc:language', 'en'); // Assuming English for now
        $metadata->appendChild($dcLanguage);

        // Manifest
        $manifest = $doc->createElement('manifest');
        $package->appendChild($manifest);

        $item = $doc->createElement('item');
        $item->setAttribute('id', 'ncx');
        $item->setAttribute('href', 'toc.ncx');
        $item->setAttribute('media-type', 'application/x-dtbncx+xml');
        $manifest->appendChild($item);

        $item = $doc->createElement('item');
        $item->setAttribute('id', 'style');
        $item->setAttribute('href', 'style.css');
        $item->setAttribute('media-type', 'text/css');
        $manifest->appendChild($item);

        foreach ($this->chapters as $index => $chapter) {
            $id = 'chapter' . ($index + 1);
            $href = 'Text/' . $id . '.xhtml';
            $item = $doc->createElement('item');
            $item->setAttribute('id', $id);
            $item->setAttribute('href', $href);
            $item->setAttribute('media-type', 'application/xhtml+xml');
            $manifest->appendChild($item);
        }

        // Spine
        $spine = $doc->createElement('spine');
        $spine->setAttribute('toc', 'ncx');
        $package->appendChild($spine);

        foreach ($this->chapters as $index => $chapter) {
            $idref = 'chapter' . ($index + 1);
            $itemref = $doc->createElement('itemref');
            $itemref->setAttribute('idref', $idref);
            $spine->appendChild($itemref);
        }

        return $doc->saveXML();
    }

    private function getTocNcx(): string
    {
        $doc = new DOMDocument('1.0', 'UTF-8');
        $doc->formatOutput = true;

        $ncx = $doc->createElement('ncx');
        $ncx->setAttribute('xmlns', 'http://www.daisy.org/z3986/2005/ncx/');
        $ncx->setAttribute('version', '2005-1');
        $doc->appendChild($ncx);

        $head = $doc->createElement('head');
        $ncx->appendChild($head);

        $metaUid = $doc->createElement('meta');
        $metaUid->setAttribute('name', 'dtb:uid');
        $metaUid->setAttribute('content', $this->uuid);
        $head->appendChild($metaUid);

        $metaDepth = $doc->createElement('meta');
        $metaDepth->setAttribute('name', 'dtb:depth');
        $metaDepth->setAttribute('content', '1');
        $head->appendChild($metaDepth);

        $docTitle = $doc->createElement('docTitle');
        $docTitle->appendChild($doc->createElement('text', $this->title));
        $ncx->appendChild($docTitle);

        $navMap = $doc->createElement('navMap');
        $ncx->appendChild($navMap);

        foreach ($this->chapters as $index => $chapter) {
            $id = 'chapter' . ($index + 1);
            $playOrder = $index + 1;

            $navPoint = $doc->createElement('navPoint');
            $navPoint->setAttribute('id', $id);
            $navPoint->setAttribute('playOrder', (string)$playOrder);
            $navMap->appendChild($navPoint);

            $navLabel = $doc->createElement('navLabel');
            $navLabel->appendChild($doc->createElement('text', $chapter['title']));
            $navPoint->appendChild($navLabel);

            $content = $doc->createElement('content');
            $content->setAttribute('src', 'Text/' . $id . '.xhtml');
            $navPoint->appendChild($content);
        }

        return $doc->saveXML();
    }
}
