# Dejima - A flexible content importer for Anki

Learning a foreign language?  It takes a lot of effort to make flash cards every time you find a new word you'd like to learn -- Dejima makes it possible for you to use your time more efficiently by automatically creating Anki flash cards from various sources you might be using to learn a new language including "Language Learning with Netflix".

**Free Software: MIT License**

## Requirements

- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) must be installed into Anki as an add-on.

## Sources Supported

- [Language Learning with Netflix](https://languagelearningwithnetflix.com/)
- Reading annotations on Onyx Boox devices.
- A source importer you write yourself -- see "Adding your own Sources" below.

You can read more about the built-in sources below.

### Language Learning with Netflix (`lln-json`)

In "Language Learning with Netflix" (LLN), you can ["save"](https://languagelearningwithnetflix.com/instructions.html) particular words or phrases.  Those phrases can be exported from LLN using your browser, and imported into Anki as flash cards.

#### Examples

Question:

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/forward_question.png)

Answer:

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/forward_answer.png)

Reverse Question (Optional):

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/reverse_question.png)

Reverse Answer (Optional):

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/reverse_answer.png)

#### How to use

1. Download your saved annotations in "Language Learning with Netflix" using the "JSON" export type:

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/lln_instructions__export_button.png)
![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/lln_instructions__export_button_actual.png)

2. Run `dejima` with the following command, replacing `My Deck Name` with the name of the deck you'd like the cards generated in, and `/path/to/export.json` with the path to the file you exported above:

```
dejima import "My Deck Name" lln-json -i /path/to/export.json
```

That's it!

### Onyx Boox Reading Annotation Exports (`boox`)

In Onyx Boox e-readers and tablets, there's an annotation mode in which you can highlight particular words or sentences, see a translation into your native language, or write notes to yourself about:

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/boox_instructions__annotation.png)

If you, too, use these for making note of unfamiliar words, you can use Dejima to convert those highlighted annotations into flash cards.

#### How to use

1. Export your saved annotations from your device and save them to the device that you are running Anki and Dejima on:

![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/boox_instructions__export_button.png)
![](http://coddingtonbear-public.s3.amazonaws.com/github/dejima/boox_instructions__export_options.png)

2. Run `dejima` with the following command, replacing `My Deck Name` with the name of the deck you'd like the cards generated in, and `/path/to/export.txt` with the path to the file you exported above:

```
dejima import "My Deck Name" boox -i /path/to/export.txt
```

## Installation

You can install dejima from pypi by running:

```
pip install dejima

```

## Adding your own sources

Dejima was built to make it easy for _me_ to easily add sources I need so hopefully that effort makes it easy for you, too!

A sample project exists at https://github.com/coddingtonbear/dejima-importer-example showing you how you might create your own importer class.

## Why is this named "Dejima"

[Anki is the Japanese word for "memorization".](https://en.wikipedia.org/wiki/Anki_(software)#:~:text=%22Anki%22%20(%E6%9A%97%E8%A8%98)%20is,methods%20employed%20in%20the%20program.) During one particular part of Japanese history, one of the few ways you could import goods into Japan was via the port of [Dejima](https://en.wikipedia.org/wiki/Dejima) in Nagasaki.
