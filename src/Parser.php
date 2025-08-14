<?php

namespace App;

use DOMDocument;

abstract class Parser
{
    public function __construct()
    {
        // No-op
    }

    /**
     * @param DOMDocument $dom
     * @return array An array of chapter URLs and titles. e.g. [['url' => 'http://...', 'title' => '...']]
     */
    abstract public function getChapterUrls(DOMDocument $dom): array;

    /**
     * @param DOMDocument $dom
     * @return DOMDocument The part of the DOM that contains the chapter content.
     */
    abstract public function findContent(DOMDocument $dom): DOMDocument;

    abstract public function extractTitle(DOMDocument $dom): string;

    abstract public function extractAuthor(DOMDocument $dom): string;

    public function getHtml(string $url): DOMDocument
    {
        $options = [
            'http' => [
                'method' => 'GET',
                'header' => "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r\n" .
                            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n" .
                            "Accept-Language: en-US,en;q=0.9\r\n"
            ]
        ];
        $context = stream_context_create($options);
        $html = @file_get_contents($url, false, $context);

        if ($html === false) {
            $error = error_get_last();
            throw new \Exception("Failed to fetch URL: $url. Error: " . ($error['message'] ?? 'Unknown error'));
        }

        $dom = new DOMDocument();
        // Suppress warnings from invalid HTML
        @$dom->loadHTML($html);

        return $dom;
    }
}
