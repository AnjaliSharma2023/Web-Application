Readme

https://github.com/bizzlebin/team_6/blob/master/resources/readme.txt

https://github.com/bizzlebin/team_g/blob/master/resources/readme.txt

***

By Jeremiah Thomas

***

Created 2021-01-19

+++

Instead of writing another spec or essay, I am linking to a bunch of tips and resources in this readme and/or including them in the directory. Keep in mind that although some of these are long, they are *far* shorter than the alternatives (eg, the UEWSG is ≈ 50 pages, the Chicago Manual Of Style ≈ 1000(!)). In general, they should make things much, much easier and simpler. If you have questions or more ideas, please contact me in the appropriate channels.

+++
General

• Always read the readme(s) first!
• Use a powerful text editor (eg, Notepad++) with soft line wrapping and dark mode—you will spare your sanity *and* your eyes!
• Use a well-designed monospaced font; I recommend, in order of best first (easy to read, obvious O vs 0, free, etc): Cousine, Liberation Mono, DejaVu Sans Mono, Hack, and Andale Mono.
• Do not spam the group e-mail; use Slack as the first option or e-mail me if you have something that cannot wait and/or needs to be private.
• Proofread your work; we'll proofread the deliverables as a separate step but you should take humility in even your smallest contributions.

+++
Python

• Follow all formats below (eg, use tabs, NKCF-style function names: the specs are quite thorough and input_int.py is a great example of a compliant program).
• Use f-strings—no """.format()""" mess!
• Try to use type annotations and verify your code via mypy.

+++
Git

• Most of your work can be sent directly from Git.
• Fetch frequently so you have the most up-to-date copy; you can fetch to (or work in) a branch so you don't lose your work.
• Make sure *not* to overwrite anything you don't have permission to; read Roles for more info.
• Commit whenever you have something meaningful to add; don't be afraid to make a small commit if it is a substantive change.
• Filenames are case-insensitive unless you change a config setting in your local repo: set """ignorecase = false"""; this shouldn't matter for our project but do take note for future projects.
• Remember to use the commit message styling in the NKMF!
• Consider adding cache files/folders to your exclude file so you don't accidentally commit them; common examples include:
•• .idea/
•• .mypy_cache/
•• .pytest_cache/
•• __pycache__/

+++
GitHub

• Do not add any special features to the repo (eg, a wiki); I've tested most of these and they're...subpar and generally much more trouble than they're worth.
• If you edit directly in GitHub, remember to change the editor settings to "Tabs", "4" (optional), and "Soft wrap".
• Make sure that you have GitHub Desktop—if you can stand to use it—set to *honor* line endings (eg, CRLF), encodings, etc: this is *not* its default, strangely.

+++
UEWSG

• Visit the main site at http://uewsg.org .
• The UEWSG is a replacement for the MLA and other style guides which, as you may know, are woefully inadequate and full of ambiguities, exceptions, and contradictions.
• In the latest version (0.2.0), you basically need to know "UTF-8, CRLF, and snake_case filenames" from chapter 2, understand 3.1 (Names And Titles), 3.2 (Abbreviations), and 3.5 (Math) from chapter 3, understand the gist of the markers and syntax for chapter 4 (particularly that bulleted lists need a literal bullet character(s)), and remember "tabs" for chapter 5; that should be the "just barely good enough" rundown of it!
• You can skim the rest of the UEWSG, but be familiar with what it contains and how to look things up (eg, the TOC or your browser's text search).
• Feel free to use it for other projects and spread the word—let's continue the push to get rid of the MLA!

+++
NKMF

• All documents must be in this format and everything I upload will be so by default; use any of the document headers for a quick reference.
• We'll mostly be using the NKMF header for our documents; you need to be familiar with the general rules, the general layout, and the first 3 parts of the header but you can skim over the rest of the spec.
• Note the aside containing the Git commit message format, generally "+|=|- [Title] (description of change)".
• The NKMF is a private draft document from another country, albeit one *very* far along in development; if you want to use it on another project, please e-mail me so I can give you the latest version and/or the eventual URL.

+++
NKCF

• All code must be in this format; it is also a private draft so please contact me if you need a more updated version in a year or two!