# Multitool
A file conversion/manipulation software for corpus linguistics.

See the [Github's wiki](https://github.com/DoReCo/multitool/wiki) for documentation.

## 0. Readme updates
(François Delafontaine: Lyon, 27-01-2020)

## 1. Context
The *multitool* has been started around 2015 to anonymize and convert files for the [OFROM](http://www11.unine.ch/) corpus (at Neuchatel, Switzerland). Initially in C++, it was reworked between 2016-9 in the ANR-DFG [SegCor](segcor.cnrs.fr) project (at Orleans, France) and translated in Python. It is now and since 2019 being developped within the ANR-DFG [DoReCo](http://www.doreco.info/) project (at Lyon, France). 

## 2. Objectives
While core objectives are the conversion and manipulation of files in the context of corpus linguistics (notably oral linguistics), some precisions are needed.
But first: *conversion* means changing a file's format. A *format* is the way information is stored in the file. We will generally use the software or collection associated with a format to designate the format itself. *Elan-to-Praat* for example means converting from the '.eaf' format to the '.TextGrid' format. Finally *manipulation* means operations on the stored information itself: merging, anonymization, inter-rater agreement, etc. 
In details, the objectives are:
1. An "X-to-Y" conversion: meaning conversion should be possible from any supported format to any other supported format (see [Pepper](https://corpus-tools.org/pepper/)'s swiss-army knife approach).
2. A *lossless* conversion: meaning that as little information should be lost during conversion as is feasible. 
3. Accessibility: meaning that the package should be available (a) for automatic integration, (b) through command prompt and (c) through a dedicated graphical interface.
4. More accessibility: meaning that the package should require as few third-party libraries as possible, be easy to understand and to expand (by users adding their own scripts).
This software's public (in corpus linguistics) is expected to have little to no experience with code. More advanced users are expected to prefer [Pepper](https://corpus-tools.org/pepper/). 

## 3. Limitations
No versioning has been yet set in place.
* Only a barebone user interface (console and graphical) has been put in place.
* Likewise, scripts don't integrate error messages.
* Current supported formats are. 'Praat (.TextGrid)', 'Elan (.eaf)', 'Exmaralda (.exb)', 'Pangloss (.xml)', 'TEI (.tei)'.
* Scripts available in 'tools' should be considered deprecated by default.
Testing has been limited and users should expect potential errors. TEI import is still in development. 

## 4. Package
In its Python version, the *multitool* is considered as a package to import as is. That package corresponds to the `conversion_data` folder. A `Multitool.pyw` file will serve as a dedicated user interface for using that package as a stand-alone.
The package is structured as follows:
* 'conversion' : contains all the conversion scripts (and the 'Transcription' class).
* 'interface' : contains all files for the dedicated user interface.
* 'tools' : contains all the manipulation scripts.
The *conversion* folder should contain a 'Transcription.py' file and a set of 'fromX.py' and 'toX.py' files (for import and export respectively). The *interface* folder should contain a 'Collection.py' file. 

## 5. How does it work?
The *multitool* is built around a `Transcription` class used for "universal" information storage: all information from all the supported formats should fit in. Import scripts instantiate a Transcription object and fill it with the file's information; export scripts use a Transcription object to write a file:
    X -fromX-> Transcription -toY-> Y
Manipulations are expected to operate on Transcription objects:
    X -fromX-> Transcription -manipulation-> Transcription -toY-> Y
In practice this can vary, as manipulations are open and dependent on the user's needs. 

The `Transcription` class is divided in (a) *data* and (b) *metadata*.
(5a) `Data` is, for oral linguistics, what corresponds to a transcription. A transcription is text aligned to sound. The alignment relies on time points (`time boundaries` or `timestamps`). A set composed of a given text and two time boundaries (its start and end points relative to sound) is called a `Segment`: technically any arbitrary unit generated that way. *Segments* might not be linguistic units, and might not be units at all (and conversely, a linguistic unit like the *pause* might have no corresponding segment). A set of segments is called a `Tier` and a set of *tiers* corresponds to the whole *transcription*.
We don't claim here that all *tiers*, that is, all sets of segments, are linguistic *transcriptions*. They can also represent translations, annotations, etc. Tiers, like segments, are type-neutral. 
(5b) `Metadata` is, for corpus linguistics, all information around the transcription: where, when, who, how... We divide it here in four categories:
* `Corpus`: metadata about the corpus or projects in which the transcription exists
* `Transcript`: metadata about the transcription itself. Name, ownership, but also activity, language, etc.
* `Recording`: metadata about the sound. Usually links to audio/video files.
* `Speakers`: metadata about the recorded participants. Name, age, occupation, etc.

The `Transcription` structure therefore is:
```
class Transcription()
    name = string; start = float; end = float
    format = string
    class Metadata()
        class Corpus()
        class Recording()
        class Transcript()
        list class Speakers()
    list class Tier()
        name = string; start = float; end = float
        metadata = dictionary
        list class Segment()
            content = string; start = float; end = float
            metadata = dictionary
```
*Start* and *end* contain the time boundaries and the content the *text*. This is how data is stored in the `Transcription` class in general, although more variables exist.

Conversion scripts follow a few conventions to harmonize their use:
1. Their main function shares the same name as the script itself. For example 'forPraat.py' has for main function 'forPraat'.
2. Import scripts ('fromX.py') have, for arguments, the file path to import and \*\*args. 
3. Import scripts always return a Transcription object.
4. Export scripts ('toX.py') have, for arguments, the file path to write, the Transcription object and \*\*args.
5. Export scripts return nothing.
6. Conversion files should not use third-party libraries. Exception is 'xml.etree.cElementTree' for XML imports.
Regarding \*\*args, the common argument is 'encoding', by default "utf-8". Some formats may have further arguments in \*\*args to customize the import/export.
While (1) should also apply to 'tools' scripts, there isn't any standardization for them.

## 6. Conclusion
The question of [file conversion](https://corflo.hypotheses.org/122) might never be answered in a satisfactory manner. Originally just an nth homemade conversion tool, our hope is this becomes an easily-accessible package for other teams/projects to use either as is, for basic use, or by being able to quickly adapt it to their requirements.
