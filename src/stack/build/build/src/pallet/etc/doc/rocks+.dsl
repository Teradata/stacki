<!--
@SI_Copyright@
                            www.stacki.com
                                 v3.0

     Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
 
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
 
2. Redistributions in binary form must reproduce the above copyright
notice unmodified and in its entirety, this list of conditions and the
following disclaimer in the documentation and/or other materials provided 
with the distribution.
 
3. All advertising and press materials, printed or electronic, mentioning
features or use of this software must display the following acknowledgement: 

	 "This product includes software developed by StackIQ" 
 
4. Except as permitted for the purposes of acknowledgment in paragraph 3,
neither the name or logo of this software nor the names of its
authors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
@SI_Copyright@
-->

<!DOCTYPE style-sheet PUBLIC "-//James Clark//DTD DSSSL Style Sheet//EN" [
<!ENTITY % html "IGNORE">
<![%html;[
<!ENTITY % print "IGNORE">
<!ENTITY docbook.dsl SYSTEM 
"/usr/share/sgml/docbook/dsssl-stylesheets/html/docbook.dsl" CDATA dsssl>
]]>
<!ENTITY % print "INCLUDE">
<![%print;[
<!ENTITY docbook.dsl SYSTEM 
"/usr/share/sgml/docbook/dsssl-stylesheets/print/docbook.dsl" CDATA dsssl>
]]>
]>

<style-sheet>

<style-specification id="print" use="docbook">
<style-specification-body> 

;;
;; Stackiq Changes
;;

(define (first-page-inner-footer gi)
	(make external-graphic
		entity-system-id: "images/roll-stackiq-small.png"
		notation-system-id: "PNG"))

(define (page-inner-footer gi)
	(make external-graphic
		entity-system-id: "images/roll-stackiq-small.png"
		notation-system-id: "PNG"))

(define %title-font-family%
  "Helvetica")
(define %body-font-family%
  "Helvetica")
(define %admon-font-family%
  "Helvetica")
(define %visual-acuity%
  "presbyopic")
(define %admon-graphics%
  #f)
;; 
;; DocBook Style Sheet for use in the Rocks Cluster Distribution project.
;; Based on ldp.dsl for Ganglia (UC Berkeley), 
;; based on the stylesheet for the Linux Documentation Project.
;;

;; ==============================
;; customize the print stylesheet
;; ==============================

(declare-characteristic preserve-sdata?
  ;; this is necessary because right now jadetex does not understand
  ;; symbolic entities, whereas things work well with numeric entities.
  "UNREGISTERED::James Clark//Characteristic::preserve-sdata?"
  #f)

(define %generate-article-toc%
  ;; Should a Table of Contents be produced for Articles?
  #t)

(define (toc-depth nd)
  2)

(define %generate-article-titlepage-on-separate-page%
  ;; Should the article title page be on a separate page?
  #t)

(define %section-autolabel%
  ;; Are sections enumerated?
  #t)

(define %footnote-ulinks%
  ;; Generate footnotes for ULinks?
  #t)

(define %bop-footnotes%
  ;; Make "bottom-of-page" footnotes?
  #t)

(define %body-start-indent%
  ;; Default indent of body text
  0pi)

(define %para-indent-firstpara%
  ;; First line start-indent for the first paragraph
  0pt)

(define %para-indent%
  ;; First line start-indent for paragraphs (other than the first)
  0pt)

(define %block-start-indent%
  ;; Extra start-indent for block-elements
  0pt)

(define formal-object-float
  ;; Do formal objects float?
  #t)

(define %hyphenation%
  ;; Allow automatic hyphenation?
  #t)

(define %admon-graphics-path%
  ;; use graphics in admonitions, set their
  "./stylesheet-images/")

(define admon-graphic-default-extension ".png")

(define (book-titlepage-recto-elements)
  (list (normalize "title")
    (normalize "subtitle")
    (normalize "corpauthor")
    (normalize "authorgroup")
    (normalize "author")
    (normalize "orgname")
    (normalize "graphic")
    (normalize "edition")
    (normalize "publisher")
    (normalize "isbn")))

(define (article-titlepage-recto-elements)
  ;; elements on an article's titlepage
  ;; note: added othercredit to the default list
  (list (normalize "title")
        (normalize "subtitle")
        (normalize "authorgroup")
        (normalize "author")
        (normalize "othercredit")
        (normalize "copyright")
        (normalize "releaseinfo")
        (normalize "pubdate")
        (normalize "revhistory")
        (normalize "abstract")))


</style-specification-body>
</style-specification>


<!--
;; ===================================================
;; customize the html stylesheet; borrowed from Cygnus
;; at http://sourceware.cygnus.com/ (cygnus-both.dsl)
;; ===================================================
-->

<style-specification id="html" use="docbook">
<style-specification-body> 

(declare-characteristic preserve-sdata?
  ;; this is necessary because right now jadetex does not understand
  ;; symbolic entities, whereas things work well with numeric entities.
  "UNREGISTERED::James Clark//Characteristic::preserve-sdata?"
  #f)

(element br
	;; declare the linebreak element
	(make empty-element gi: "BR"))

(define %generate-legalnotice-link%
  ;; put the legal notice in a separate file
  #t)

(define %admon-graphics-path%
  ;; use graphics in admonitions, set their
  "./stylesheet-images/")

(define %admon-graphics%
  #t)

(define %funcsynopsis-decoration%
  ;; make funcsynopsis look pretty
  #t)

(define %html-ext%
  ;; when producing HTML files, use this extension
  ".html")

(define %generate-book-toc%
  ;; Should a Table of Contents be produced for books?
  #t)

(define %generate-article-toc% 
  ;; Should a Table of Contents be produced for articles?
  #t)

(define %generate-part-toc%
  ;; Should a Table of Contents be produced for parts?
  #t)

(define %generate-book-titlepage%
  ;; produce a title page for books
  #t)

(define %generate-article-titlepage%
  ;; produce a title page for articles
  #t)

(define (chunk-skip-first-element-list)
  ;; forces the Table of Contents on separate page
  '())

(define (list-element-list)
  ;; fixes bug in Table of Contents generation
  '())

(define %root-filename%
  ;; The filename of the root HTML document (e.g, "index").
  "index")

(define %shade-verbatim%
  ;; verbatim sections will be shaded if t(rue)
  #t)

(define %use-id-as-filename%
  ;; Use ID attributes as name for component HTML files?
  #t)

(define %graphic-extensions%
  ;; graphic extensions allowed
  '("gif" "png" "jpg" "jpeg" "tif" "tiff" "eps" "epsf" ))

(define ($admon-graphic$ #!optional (nd (current-node)))
  ;; Admonition graphic file
  (cond ((equal? (gi nd) (normalize "tip"))
         (string-append %admon-graphics-path% "tip.png"))
        ((equal? (gi nd) (normalize "note"))
         (string-append %admon-graphics-path% "note.png"))
        ((equal? (gi nd) (normalize "important"))
         (string-append %admon-graphics-path% "important.png"))
        ((equal? (gi nd) (normalize "caution"))
         (string-append %admon-graphics-path% "caution.png"))
        ((equal? (gi nd) (normalize "warning"))
         (string-append %admon-graphics-path% "warning.png"))
        (else (error (string-append (gi nd) " is not an admonition.")))))

(define admon-graphic-extension ".png")

(define %graphic-default-extension% 
  "png")

(define %section-autolabel%
  ;; For enumerated sections (1.1, 1.1.1, 1.2, etc.)
  #t)

(define (toc-depth nd)
  ;; more depth (2 levels) to toc; instead of flat hierarchy
  ;; Rocks: if we are in a chapter, give 3, otherwise 2.
  (if (string=? (gi nd) (normalize "chapter"))
  	3
  	2))

(element emphasis
  ;; make role=strong equate to bold for emphasis tag
  (if (equal? (attribute-string "role") "strong")
     (make element gi: "STRONG" (process-children))
     (make element gi: "EM" (process-children))))

(define (book-titlepage-recto-elements)
  (list (normalize "title")
    (normalize "subtitle")
    (normalize "corpauthor")
    (normalize "authorgroup")
    (normalize "author")
    (normalize "orgname")
    (normalize "graphic")
    (normalize "copyright")
    (normalize "legalnotice")
    (normalize "releaseinfo")
    (normalize "publisher")
    (normalize "isbn")))

(define (article-titlepage-recto-elements)
  ;; elements on an article's titlepage
  ;; note: added othercredit to the default list
  (list (normalize "title")
        (normalize "subtitle")
        (normalize "authorgroup")
        (normalize "author")
        (normalize "othercredit")
        (normalize "releaseinfo")
        (normalize "copyright")
        (normalize "pubdate")
        (normalize "revhistory")
        (normalize "abstract")))

(mode article-titlepage-recto-mode

 (element contrib
  ;; print out with othercredit information; for translators, etc.
  (make sequence
    (make element gi: "SPAN"
          attributes: (list (list "CLASS" (gi)))
          (process-children))))

 (element othercredit
  ;; print out othercredit information; for translators, etc.
  (let ((author-name  (author-string))
        (author-contrib (select-elements (children (current-node))
                                          (normalize "contrib"))))
    (make element gi: "P"
         attributes: (list (list "CLASS" (gi)))
         (make element gi: "B"  
              (literal author-name)
              (literal " - "))
         (process-node-list author-contrib))))
)

(define (article-title nd)
  (let* ((artchild  (children nd))
         (artheader (select-elements artchild (normalize "artheader")))
         (artinfo   (select-elements artchild (normalize "articleinfo")))
         (ahdr (if (node-list-empty? artheader)
                   artinfo
                   artheader))
         (ahtitles  (select-elements (children ahdr)
                                     (normalize "title")))
         (artitles  (select-elements artchild (normalize "title")))
         (titles    (if (node-list-empty? artitles)
                        ahtitles
                        artitles)))
    (if (node-list-empty? titles)
        ""
        (node-list-first titles))))


;; Redefinition of $verbatim-display$
;; Origin: dbverb.dsl
;; Different foreground and background colors for verbatim elements
;; Author: Philippe Martin (feloy@free.fr) 2001-04-07

(define ($verbatim-display$ indent line-numbers?)
  (let ((verbatim-element (gi))
        (content (make element gi: "PRE"
                       attributes: (list
                                    (list "CLASS" (gi)))
                       (if (or indent line-numbers?)
                           ($verbatim-line-by-line$ indent line-numbers?)
                           (process-children)))))
    (if %shade-verbatim%
        (make element gi: "TABLE"
              attributes: (shade-verbatim-attr-element verbatim-element)
              (make element gi: "TR"
                    (make element gi: "TD"
                          (make element gi: "FONT" 
                                attributes: (list
                                             (list "COLOR" (car 
(shade-verbatim-element-colors
                                                                 
verbatim-element))))
                               content))))
        content)))

;;
;; Customize this function
;; to change the foreground and background colors
;; of the different verbatim elements
;; Return (list "foreground color" "background color")
;;
(define (shade-verbatim-element-colors element)
  (case element
    (("SYNOPSIS") (list "#000000" "#6495ED"))
    ;; ...
    ;; Add your verbatim elements here
    ;; ...
    (else (list "#000000" "#E0E0E0"))))

(define (shade-verbatim-attr-element element)
  (list
   (list "BORDER" 
	(cond
		((equal? element (normalize "SCREEN")) "0")
		(else "0")))
   (list "BGCOLOR" (car (cdr (shade-verbatim-element-colors element))))
   (list "WIDTH" ($table-width$))))

;; End of $verbatim-display$ redefinition

;; Begin Rocks css customization
(define %stylesheet% "rocksplus.css")
(define %stylesheet-type% "text/css")
;; End Rocks css customization

</style-specification-body>
</style-specification>

<external-specification id="docbook" document="docbook.dsl">

</style-sheet>
