<?php

namespace App\Parsers;

use App\Parser;
use DOMDocument;
use DOMXPath;

class ArchiveOfOurOwnParser extends Parser
{
    public function getChapterUrls(DOMDocument $dom): array
    {
        $xpath = new DOMXPath($dom);
        $chapters = [];

        // Check if it's a multi-chapter work
        $chapterNodes = $xpath->query("//ol[@class='chapter index group']/li/a");

        if ($chapterNodes->length > 0) {
            foreach ($chapterNodes as $node) {
                $chapters[] = [
                    'url' => $node->getAttribute('href'),
                    'title' => $node->nodeValue,
                ];
            }
        }
        // For single chapter works, this will be empty, and the controller
        // should use the main DOM for content extraction.

        return $chapters;
    }

    public function findContent(DOMDocument $dom): DOMDocument
    {
        $xpath = new DOMXPath($dom);
        $contentNode = $xpath->query("//div[@id='chapters']")->item(0);

        // Create a new DOM document to hold the content
        $contentDom = new DOMDocument();
        if ($contentNode) {
            // Import the node into the new document
            $importedNode = $contentDom->importNode($contentNode, true);
            $contentDom->appendChild($importedNode);
        }

        return $contentDom;
    }

    public function extractTitle(DOMDocument $dom): string
    {
        $xpath = new DOMXPath($dom);
        $titleNode = $xpath->query("//h2[contains(@class, 'title')]")->item(0);
        return $titleNode ? trim($titleNode->nodeValue) : '';
    }

    public function extractAuthor(DOMDocument $dom): string
    {
        $xpath = new DOMXPath($dom);
        $authorNode = $xpath->query("//a[@rel='author']")->item(0);
        return $authorNode ? trim($authorNode->nodeValue) : '';
    }
}
