# OCR Miner - Anki Card Type

Sentence mining card type for Anki, designed for use with [Yomitan](https://github.com/themoeway/yomitan).

## Importing the Card Type

### Option 1: Install the .apkg (Recommended)

1. Open Anki
2. Go to **File > Import** and select `coles-sentence-mining.apkg`
3. After importing, you can **delete the example deck** if you don't want it — the card type (note type) will remain available in Anki

> [!Note]
> This is the recommended method as it imports the card type with all fields, styling, and templates pre-configured.

### Option 2: Manual Setup

1. In Anki, press `Ctrl+Shift+N` (or **Tools > Manage Note Types**)
2. Click **Add**
3. Choose **Add: Cloze** (not Basic)
4. Name it `coles-sentence-mining`
5. Add the following **fields**: `Full Sentence Hidden`, `Sentence`, `Sentence Cloze Prefix`, `Sentence Cloze Suffix`, `Translation`, `Word`, `Reading`, `Definition`, `Audio`, `Image`, `Notes`
6. Copy the contents of `front.html` into the **Front Template**, `back.html` into the **Back Template**, and `style.css` into the **Styling** section

## Required Add-on

This card type uses audio fields that work best with:

- **HyperTTS** ([AnkiWeb ID: `111623432`](https://ankiweb.net/shared/info/111623432))
  - Install via **Tools > Add-ons > Get Add-ons** and enter `111623432`
  - Or install directly from [ankiweb.net/shared/info/111623432](https://ankiweb.net/shared/info/111623432)

HyperTTS generates text-to-speech audio for your target language, which will populate the **Audio** field on your cards.

## Connecting with Yomitan

In Yomitan, configure your Anki card format to map its variables to this card type's fields. The field mapping (`fields.json`) is:

| Yomitan Variable | Card Field |
|---|---|
| `sentence` | `Full Sentence Hidden` |
| `cloze-body` | `Sentence` |
| `cloze-prefix` | `Sentence Cloze Prefix` |
| `cloze-suffix` | `Sentence Cloze Suffix` |
| `glossary-plain-no-dictionary` | `Translation` |
| `expression` | `Word` |
| `reading` | `Reading` |
| `glossary` | `Definition` |
| `audio` | `Audio` |
| `clipboard-image` | `Image` |
| `pitch-accents` | `Notes` |

### Yomitan Setup Steps

1. Open Yomitan's settings
2. Go to **Anki** > **Configure Anki card format**
3. Select the note type **coles-sentence-mining** (or whatever you named it)
4. Set the **fields** using the mapping above
5. Save and test with a mined sentence
