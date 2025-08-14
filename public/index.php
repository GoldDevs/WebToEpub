<?php

spl_autoload_register(function ($class) {
    $prefix = 'App\\';
    $base_dir = __DIR__ . '/../src/'; // Relative to public/
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

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['url'])) {
    try {
        $url = $_POST['url'];
        if (!filter_var($url, FILTER_VALIDATE_URL)) {
            throw new Exception('Invalid URL provided.');
        }

        // 1. Get the parser for the URL
        $parser = ParserFactory::create($url);

        // 2. Get the initial page DOM
        $initialDom = $parser->getHtml($url);

        // 3. Extract metadata
        $title = $parser->extractTitle($initialDom);
        $author = $parser->extractAuthor($initialDom);

        // 4. Get chapter URLs
        $chapterUrls = $parser->getChapterUrls($initialDom);
        if (empty($chapterUrls)) {
            // Handle single chapter stories
            $chapterUrls = [['url' => $url, 'title' => $title]];
        }

        // 5. Fetch and parse each chapter
        $chapters = [];
        foreach ($chapterUrls as $chapterInfo) {
            // Make URL absolute
            $chapterUrl = $chapterInfo['url'];
            if (!preg_match('/^http/', $chapterUrl)) {
                 $chapterUrl = 'https://archiveofourown.org' . $chapterUrl;
            }

            $chapterDom = $parser->getHtml($chapterUrl);
            $chapters[] = [
                'title' => $chapterInfo['title'],
                'content' => $parser->findContent($chapterDom),
            ];
        }

        // 6. Pack the EPUB
        $packer = new EpubPacker($title, $author, $chapters);
        $epubFile = $packer->createEpub();

        // 7. Send the file to the browser
        header('Content-Type: application/epub+zip');
        header('Content-Disposition: attachment; filename="' . basename($title) . '.epub"');
        header('Content-Length: ' . filesize($epubFile));
        readfile($epubFile);

        // 8. Clean up
        unlink($epubFile);
        exit;

    } catch (Exception $e) {
        $error = $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebToEpub PHP</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
        input[type="url"] { width: 80%; padding: 10px; }
        input[type="submit"] { padding: 10px 20px; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>WebToEpub PHP</h1>
    <p>Enter the URL of a story from a supported website to convert it to an EPUB file.</p>
    <p>Currently supported: archiveofourown.org</p>

    <form action="index.php" method="POST">
        <label for="url">Story URL:</label><br>
        <input type="url" id="url" name="url" required placeholder="https://archiveofourown.org/works/...">
        <input type="submit" value="Create EPUB">
    </form>

    <?php if (isset($error)): ?>
        <p class="error">Error: <?php echo htmlspecialchars($error); ?></p>
    <?php endif; ?>
</body>
</html>
