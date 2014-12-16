/*
 * jQuery Highlight plugin
 *
 * Based on highlight v3 by Johann Burkard
 * http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html
 *
 * Copyright (c) 2009 Bartek Szopka
 *
 * Licensed under MIT license.
 */
jQuery.extend({highlight:function(e,t,n,r){if(e.nodeType===3){var i=e.data.match(t);if(i){var s=document.createElement(n||"span");s.className=r||"highlight";var o=e.splitText(i.index);o.splitText(i[0].length);var u=o.cloneNode(true);s.appendChild(u);o.parentNode.replaceChild(s,o);return 1}}else if(e.nodeType===1&&e.childNodes&&!/(script|style)/i.test(e.tagName)&&!(e.tagName===n.toUpperCase()&&e.className===r)){for(var a=0;a<e.childNodes.length;a++){a+=jQuery.highlight(e.childNodes[a],t,n,r)}}return 0}});jQuery.fn.unhighlight=function(e){var t={className:"highlight",element:"span"};jQuery.extend(t,e);return this.find(t.element+"."+t.className).each(function(){var e=this.parentNode;e.replaceChild(this.firstChild,this);e.normalize()}).end()};jQuery.fn.highlight=function(e,t){var n={className:"highlight",element:"span",caseSensitive:false,wordsOnly:false};jQuery.extend(n,t);if(e.constructor===String){e=[e]}e=jQuery.grep(e,function(e,t){return e!=""});e=jQuery.map(e,function(e,t){return e.replace(/[-[\]{}()*+?.,\\^$|#\s]/g,"\\$&")});if(e.length==0){return this}var r=n.caseSensitive?"":"i";var i="("+e.join("|")+")";if(n.wordsOnly){i="\\b"+i+"\\b"}var s=new RegExp(i,r);return this.each(function(){jQuery.highlight(this,s,n.element,n.className)})}
