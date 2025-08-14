<?php

namespace App;

use App\Parsers\ArchiveOfOurOwnParser;
use InvalidArgumentException;

class ParserFactory
{
    public static function create(string $url): Parser
    {
        $host = parse_url($url, PHP_URL_HOST);

        if (str_contains($host, 'archiveofourown.org')) {
            return new ArchiveOfOurOwnParser();
        }

        throw new InvalidArgumentException("No parser found for host: $host");
    }
}
