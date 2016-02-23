r"""  mathquizXml.py | 2001-03-21       | Don Taylor
                       2004 Revisions   | Andrew Mathas
                       2010 Version 4.5 | Updated and streamlined 
                       2012 Version 4.6
                       2016 Version 4.7

     Convert an XML quiz description to a tree of Python objects
     whose structure reflects the DTD (mathquiz.dtd)

     Command line options:

       -d  debug

     Known bugs:
       The __str__ methods do not handle unicode

     Requires:
       Python 2.0

     History:
       26 Jan 03  Add support for <meta> and <link> elements
       May 2004   Expanded allowable xml tags and syntax

#*****************************************************************************
#       Copyright (C) 2004-2016 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the MathQuiz system.
#
# Copyright (C) 2004-2010 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
# <Donald.Taylor@sydney.edu.au>
#*****************************************************************************
"""
import sys, getopt
from xml.sax import handler, make_parser

DEBUG = 0

def main():
  global DEBUG

  def fail(msg = None):
    if msg:
      print msg
    print 'Usage: %s [-d] <xml-file>' % sys.argv[0]
    sys.exit(1)

  if len(sys.argv) < 2:
    fail()

  try:
    opts, files = getopt.getopt(sys.argv[1:],'d')
  except getopt.GetoptError,e:
    print >> sys.stderr, e
    sys.exit(1)
    
  if not files:
    fail()
  for opt in opts:
    if opt[0] == '-d':
      DEBUG = 1

  try:
    f = open(files[0])
  except IOError,e:
    print >> sys.stderr, e
    sys.exit(1)

  quiz = DocumentTree(f)
  f.close()

  # The default action is to write out the file as xml
  # This should have the same content as the input, but
  # may differ in the order of attributes and the amount
  # of white space.

  quiz.accept(xmlWriter())

def DocumentTree(infile):
  parser = make_parser()
  dh = XMLaction()
  parser.setContentHandler(dh)
  parser.setErrorHandler(dh)
  parser.parse(infile)
  #parser.close()
  return dh.root

def addAttrs(lst,attrs):
  lst.append(attrs)

#@-- Not presently used
def asString(tag,lst):
  if lst:
    s = tag+':\n'
    for slot in lst:
       s += '%s\n' % slot
  else:
     s = ''
  return s

def strval(ustr):
  if type(ustr) == type(u''):
    str = ''
    for c in ustr:
      str += chr(ord(c))
  else:
    str = ustr
  return str

# -----------------------------------------------------
# The HandlerBase class inherits from:
#  DocumentHandler, DTDHandler, EntityResolver, ErrorHandler
# -----------------------------------------------------
class SAXinterface( handler.ContentHandler ):
  "Provides generic callback methods for the SAX interface"

  def __init__(self):
    self.level = 0
    self.text = ''
    # self.text accumulates character data.  It is set to
    # a null string by startElement but it may persist
    # after the corresponding endElement fires.

  def startElement(self, name, attrs):
    self.text= ''
    self.level += 1
    method = name + "_START"
    if DEBUG:
      print 'Looking for', method
    if hasattr(self,method):
      getattr(self,method)(attrs)
    else:
      self.default_START(name,attrs)

  def characters(self,chars): #data,start,length):
    if self.level > 0:
      self.text +=chars # cdata[start:start+length]

  def endElement(self,name):
    self.level = self.level-1
    method = name + "_END"
    if hasattr(self,method):
      getattr(self,method)()
    else:
      self.default_END(name)

#  def ignorableWhitespace(self,cdata,start,length):
#    self.characters(cdata,start,length)

#  def processingInstruction(self,target,data):
#    print "<?"+target+" "+data+"?>"

  def default_START( self, name, attrs ):
    if DEBUG:
      print >> sys.stderr, 'START:', name

  def default_END( self, name ):
    if DEBUG:
      print >> sys.stderr, 'END:', name

  def error(self, e):
    raise e

  def fatalError(self, e):
    raise e

# -----------------------------------------------------
class XMLaction( SAXinterface ):
  """provides callbacks for all the entities in mathquiz.dtd.
     These methods manage the construction of the document tree.

     The SAXinterface provides a dictionary of attributes when it
     calls xxx_START.  The value of a given key can be
     retrieved by attrs.get('keyname','default')

     PCDATA is accumulated in self.text
     self.position keeps track of where we are in the tree

     Provide a list for all child elements of the form xxx*

     The quiz files themselves may need to use the <![CDATA[ ... ]]>
     construction to include HTML markup in the text sections.
  """
  def __init__(self):
    SAXinterface.__init__(self)
    self.root = Node()
    self.position = self.root

  def quiz_START( self, attrs ):
    self.root = Quiz()
    self.position = self.root
    self.position.title=attrs.get('title','default')
    self.position.breadCrumb=attrs.get('breadCrumb','default')
    self.position.src=attrs.get('src','default')

  def meta_START( self, attrs ):
    addAttrs(self.position.metaList,attrs)
    if DEBUG:
	print "META start %s\n" % attrs

  def link_START( self, attrs ):
    addAttrs(self.position.linkList,attrs)

  def quizlistitem_START( self, attrs ):
    addAttrs(self.position.quizList,attrs)

  def course_START( self, attrs ):
    addAttrs(self.position.course,attrs)

  def question_START( self, attrs ):
    q = Question(self.position)
    self.position.questionList.append(q)
    self.position = q

  def text_END( self ):
    self.position.setText(self.text)

  def choice_START( self, attrs ):
    if self.position.answer:
      print >> sys.stderr, "Processing halted. Multiple <choice>/<answer> tags"
      sys.exit(1)
    self.position.answer=Choice(self.position,attrs.get('type'),attrs.get('cols'))
    self.position = self.position.answer

  def answer_START( self, attrs ):
    if self.position.answer:
      print >> sys.stderr, "Processing halted. Multiple <choice>/<answer> tags"
      sys.exit(1)
    self.position.answer = Answer(self.position,attrs.get('value'))
    self.position = self.position.answer

  def tag_END( self ):
    self.position.tag = self.text.strip()

  def discussion_START( self, attrs ):
    d = Discussion(self.position,attrs.get('heading'))
    self.position.discussionList.append(d)
    self.position = d

  def discussion_END( self ):
    self.position = self.position.parent

  def item_START( self, attrs ):
    r = Item(self.position,attrs.get('expect'))
    self.position.itemList.append(r)
    self.position = r

  def response_END( self ):
    self.position.response = self.text.strip()

  def whenRight_END( self ):
    self.position.whenTrue = self.text.strip()

  def whenWrong_END( self ):
    self.position.whenFalse = self.text.strip()

  def item_END( self ):
    self.position = self.position.parent

  def answer_END( self ):
    self.position = self.position.parent

  def choice_END( self ):
    self.position = self.position.parent

  def question_END( self ):
    self.position = self.position.parent

  def quiz_END( self ):
    if DEBUG:
      print 'level =', self.level

# -----------------------------------------------------
#  DTD structure
# -----------------------------------------------------

# Each node of the document tree keeps a reference to its
# parent node in self.parent except for the root, which
# defaults to None

class Node:
  def __init__(self,parent = None):
    self.parent = parent
    if DEBUG:
      if parent:
        print self.__class__.__name__, parent.__class__.__name__
      else:
        print self.__class__.__name__

  def accept(self,visitor):
    pass

  def broadcast(self,visitor):
    pass

  def __str__(self):
    return ''


class Quiz(Node):
  """<!ELEMENT quiz (title, breadCrumb, meta*, link*, question*)>
     <!ELEMENT title (#PCDATA)>
  """
  def __init__(self):
    Node.__init__(self)
    self.metaList = []
    self.linkList = []
    self.quizList = []
    self.course= []
    self.discussionList = []
    self.questionList = []

  def accept(self,visitor):
    visitor.forQuiz(self)

  def broadcast(self,visitor):
    for node in self.questionList:
      node.accept(visitor)  

  def __str__(self):
    s = 'Quiz: %s\n' % self.title
    for p in self.questionList:
      s += '%s\n' % p
    return s

class Discussion(Node):
  """<!ELEMENT discussion (#PCDATA)>
     <!ATTLIST dicussion heading #PCDATA #required>
  """
  def __init__(self,parent,heading="Discussion"):
    Node.__init__(self,parent)
    self.discussion=""
    self.heading=heading

  def accept(self,visitor):
    visitor.forDiscussion(self)

  def broadcast(self,visitor):
    for node in self.questionList:
      node.accept(visitor)  

  def setText(self,text):
    self.discussion=text.strip()

  def __str__(self):
    return 'Discussion('+self.heading+'):'+self.discussion

class Question(Node):
  """<!ELEMENT question (text, (choice|answer))>
     <!ELEMENT text (#PCDATA)>
  """
  def __init__(self, parent):
    Node.__init__(self,parent)
    self.question = ""  # The text of the question
    self.answer = None  # Can be a Node of class Answer OR Choice

  def setText(self,text):
    self.question = text.strip()

  def accept(self,visitor):
    visitor.forQuestion(self)

  def broadcast(self,visitor):
    if self.answer:
      self.answer.accept(visitor)

  def __str__(self):
    return 'Question: '+self.question+'\n'+str(self.answer)


class Choice(Node):
  """<!ELEMENT choice (item*)>
     <!ATTLIST choice type (single|multiple) #REQUIRED
                           cols #CDATA       #REQUIRED 
     >
  """
  def __init__(self,parent,type,cols):
    Node.__init__(self,parent)
    self.itemList = []
    # --
    self.type = type
    self.cols = int(cols)

  def accept(self,visitor):
    visitor.forChoice(self)

  def broadcast(self,visitor):
    for node in self.itemList:
      node.accept(visitor)

  def __str__(self):
    s = "Choices:\n"
    for p in self.itemList:
      s += '%s\n' % str(p)
    return s


class Answer(Node):
  """<!ELEMENT answer (tag?, whenRight, whenWrong)>
     <!ATTLIST answer value CDATA #REQUIRED>
     <!ELEMENT tag (#PCDATA)>
     <!ELEMENT whenRight (#PCDATA)>
     <!ELEMENT whenWrong (#PCDATA)>
  """
  def __init__(self,parent,value):
    Node.__init__(self,parent)
    self.tag       = ""
    self.whenTrue  = ""
    self.whenFalse = ""
    # --
    self.value     = value

  def accept(self,visitor):
    visitor.forAnswer(self)

  def __str__(self):
    s = self.value+': '
    if self.tag:
      s += self.tag
    s += '\nRight: %s Wrong:' % (self.whenTrue,self.whenFalse)
    return s

class Item(Node):
  """<!ELEMENT item (text,response?)>
     <!ATTLIST item expect (true|false) #REQUIRED>
     <!ELEMENT text (#PCDATA)>
     <!ELEMENT response (#PCDATA)>
  """
  def __init__(self,parent,expect):
    Node.__init__(self,parent)
    self.answer   = ""
    self.response = ""
    # --
    self.expect = expect

  def setText(self,text):
    self.answer = text.strip()

  def accept(self,visitor):
    visitor.forItem(self)

  def __str__(self):
    s = '%s: %s' % (self.expect,self.answer)
    if self.response:
      s += '\nResponse: ' + self.response
    return s


# =====================================================
# Visitor classes
# =====================================================

class nodeVisitor:
  """In the methods of this class, 'node' refers to the
  instance of the class calling the 'accept' method.  The
  general form of 'accept' is
  
         def accept(self,visitor):
           visitor.forXXX(self)
   
  In the method 'forXXX' of the visitor class, 'node' will
  refer to an instance of 'XXX'.
  """

  def forQuiz(self,node):
    node.broadcast(self)

  def forDiscussion(self,node):
    node.broadcast(self)

  def forQuestion(self,node):
    node.broadcast(self)

  def forChoice(self,node):
    node.broadcast(self)

  def forAnswer(self,node):
    pass

  def forItem(self,node):
    pass

# -----------------------------------------------------
class xmlWriter(nodeVisitor):

#@-- Not presently used
  def element(self,node,tag):
    print ' <%s>'  % tag
    node.broadcast(self)
    print ' </%s>' % tag

  def forQuiz(self,node):
    print '<?xml version="1.0" encoding="iso-8859-1"?>'
    print '<!DOCTYPE quiz SYSTEM "mathquiz.dtd">' 
    print '<quiz>'
    for p in node.metaList:
      s = '<meta'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print s
    for p in node.course:
      s = '<course'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print s
    for p in node.linkList:
      s = '<link'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print s
    print '<title>%s</title>' % node.title
    node.broadcast(self)
    print '</quiz>'

  def forQuestion(self,node):
    print '<question>'
    print '<text><![CDATA[%s]]></text>' % strval(node.question)
    node.broadcast(self)
    print '</question>'

  def forChoice(self,node):
    print '  <choice type="%s" cols="%s">' % (node.type, node.cols)
    node.broadcast(self)
    print '  </choice>'

  def forAnswer(self,node):
    print '    <answer value="%s">' % node.value
    if node.tag:
      print '      <tag>%s</tag>' % strval(node.tag)
    print '      <whenRight><![CDATA[%s]]></whenRight>' % strval(node.whenTrue)
    print '      <whenWrong><![CDATA[%s]]></whenWrong>' % strval(node.whenFalse)
    print '    </answer>'  
  
  def forItem(self,node):
    print '    <item expect="%s">' % node.expect
    print '      <text><![CDATA[%s]]></text>' % strval(node.answer)
    if node.response:
      print '      <response><![CDATA[%s]]></response>' % strval(node.response)
    print '    </item>'

# =====================================================
if __name__ == '__main__':
  main()

