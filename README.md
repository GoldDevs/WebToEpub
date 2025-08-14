# WebToEpub PHP Version

This is a PHP-based web application to convert web stories into EPUB files. It is a conversion of the [WebToEpub browser extension](https://github.com/dteviot/WebToEpub).

## Features

*   Convert web stories to EPUB format.
*   Simple web interface.
*   Compatible with PC (Windows, macOS, Linux) and Termux on Android.

## Supported Websites

*   **archiveofourown.org**: Fully supported.

### A Note on Adding Other Websites

This application is designed to be extensible. New parsers can be added in the `src/Parsers` directory and registered in the `ParserFactory`.

However, many modern websites use advanced bot detection techniques (like Cloudflare's JavaScript challenges) that prevent simple server-side scraping. The original browser extension works because it runs in a full browser environment. This PHP application cannot bypass these protections, as demonstrated by the attempt to add a parser for `novelbin.com`.

Therefore, only websites that do not employ such advanced bot detection can be supported.

## Requirements

*   PHP 7.4 or higher (with `php-xml`, `php-zip`, and `php-curl` extensions).
*   [Composer](https://getcomposer.org/)
*   Git

## Setup and Usage

### 1. Clone the Repository

Open your terminal or command prompt and run the following command:

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Install Dependencies

Use Composer to install the required PHP packages:

```bash
composer install
```

This will download Guzzle and create the `vendor` directory.

### 3. Run the Application

This project can be run using PHP's built-in web server. From the root directory of the project, run:

```bash
php -S localhost:8000 -t public
```

This will start a web server on port 8000. You can now open your web browser and navigate to `http://localhost:8000` to use the application.

## Usage on Termux (Android)

The same setup instructions apply to Termux on Android. You will need to install the required packages first.

1.  **Install PHP and Git:**
    ```bash
    pkg update && pkg upgrade
    pkg install php git
    ```

2.  **Install Composer:**
    Follow the official instructions on the [Composer website](https://getcomposer.org/download/) to install it in your Termux environment.

3.  **Follow the standard setup instructions above** (clone repository, install dependencies, run the server). You can then access the application from your phone's browser at `http://localhost:8000`.
