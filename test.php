<?php

spl_autoload_register(function ($class) {
    $prefix = 'App\\';
    $base_dir = __DIR__ . '/src/';
    $len = strlen($prefix);
    if (strncmp($prefix, $class, $len) !== 0) {
        return;
    }
    $relative_class = substr($class, $len);
    $file = $base_dir . str_replace('\\', '/', $relative_class) . '.php';
    if (file_exists($file)) {
        require $file;
    }
});

use App\ParserFactory;
use App\EpubPacker;

$testUrl = 'https://archiveofourown.org/works/2422325';

echo "Starting test with URL: $testUrl\n";

try {
    // 1. Get parser
    $parser = ParserFactory::create($testUrl);
    echo "Parser created successfully.\n";

    // 2. Get initial DOM
    $initialDom = $parser->getHtml($testUrl);
    echo "Initial page fetched successfully.\n";

    // 3. Extract metadata
    $title = $parser->extractTitle($initialDom);
    $author = $parser->extractAuthor($initialDom);
    echo "Metadata extracted: Title='$title', Author='$author'\n";

    if (empty($title) || empty($author)) {
        throw new Exception("Failed to extract metadata.");
    }

    // 4. Get chapter URLs
    $chapterUrls = $parser->getChapterUrls($initialDom);

    // 5. Fetch content
    $chapters = [];
    if (empty($chapterUrls)) {
        // Single chapter work
        $contentDom = $parser->findContent($initialDom);
        $chapters[] = ['title' => $title, 'content' => $contentDom];
        echo "Content for single-chapter work extracted.\n";
    } else {
        // Multi-chapter work (testing first chapter only)
        $chapterInfo = $chapterUrls[0];
        $chapterUrl = $chapterInfo['url'];
        if (!preg_match('/^http/', $chapterUrl)) {
             $chapterUrl = 'https://archiveofourown.org' . $chapterUrl;
        }
        $chapterDom = $parser->getHtml($chapterUrl);
        $contentDom = $parser->findContent($chapterDom);
        $chapters[] = ['title' => $chapterInfo['title'], 'content' => $contentDom];
        echo "First chapter content fetched successfully.\n";
    }

    if (!$chapters[0]['content']->documentElement || !$chapters[0]['content']->documentElement->hasChildNodes()) {
        throw new Exception("Failed to find content for the chapter.");
    }

    // 6. Pack the EPUB
    $packer = new EpubPacker($title, $author, $chapters);
    $epubFile = $packer->createEpub();
    echo "EPUB file created at: $epubFile\n";

    // 7. Verify file creation
    if (!file_exists($epubFile) || filesize($epubFile) === 0) {
        throw new Exception("EPUB file was not created or is empty.");
    }
    echo "EPUB file seems valid.\n";

    // 8. Clean up
    unlink($epubFile);
    echo "Cleaned up temporary file.\n";

    echo "\nTEST PASSED!\n";

} catch (Exception $e) {
    echo "\nTEST FAILED: " . $e->getMessage() . "\n";
    exit(1);
}

exit(0);
