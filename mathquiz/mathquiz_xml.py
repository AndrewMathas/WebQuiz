r"""
#*****************************************************************************
#  Copyright (C) 2004-2017 Andrew Mathas and Donald Taylor
#  University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the Math_quiz system.
#
# Copyright (C) 2004-2017 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
# <Donald.Taylor@sydney.edu.au>
#*****************************************************************************
"""

# -*- encoding: utf-8 -*-

import sys, getopt
import xml.sax 

DEBUG = False
if DEBUG:
    def Debugging(*arg):
        sys.stderr.write(' '.join('%s' % a for a in arg)+'\n')
else:
    def Debugging(*arg):
        pass

def strval(ustr):
  if type(ustr) == type(u''):
    str = ''
    for c in ustr:
      str += chr(ord(c))
  else:
    str = ustr
  return str

def ReadXMLTree(quizfile):
    parser = xml.sax.make_parser()
    quiz = QuizHandler()
    parser.setContentHandler(quiz)
    parser.setErrorHandler(quiz)
    parser.parse(quizfile)
    return quiz.root
    #parser.close()

# -----------------------------------------------------
# The HandlerBase class inherits from#:
# DocumentHandler, DTDHandler, EntityResolver, ErrorHandler
# -----------------------------------------------------
class QuizHandler(xml.sax.ContentHandler):
  """
     Provides callbacks for all the entities in mathquiz.dtd.
     These methods manage the construction of the document tree.

     The SAXinterface provides a dictionary of attributes when it
     calls xxx_start.  The value of a given key can be
     retrieved by attrs.get('keyname','default')

     PCDATA is accumulated in self.text
     self.position keeps track of where we are in the tree

     Provide a list for all child elements of the form xxx*

     The quiz files themselves may need to use the <![CDATA[ ... ]]>
     construction to include HTML markup in the text sections.
  """
  def __init__(self):
    self.level = 0
    self.text = ''
    self.root = Node()
    self.position = self.root
    # self.text accumulates character data.  It is set to
    # a null string by startElement but it may persist
    # after the corresponding endElement fires.

  def startElement(self, name, attrs):
    self.text= ''
    self.level += 1
    method = name + "_start"
    Debugging('Looking for '+ method)
    if hasattr(self,method):
      getattr(self,method)(attrs)
    else:
      self.default_start(name,attrs)

  def characters(self,chars): #data,start,length):
    if self.level > 0:
      self.text +=chars # cdata[start:start+length]

  def endElement(self,name):
    self.level = self.level-1
    method = name + "_end"
    if hasattr(self,method):
      getattr(self,method)()
    else:
      self.default_end(name)

#  def ignorable_whitespace(self,cdata,start,length):
#    self.characters(cdata,start,length)

#  def processing_instruction(self,target,data):
#    print "<?"+target+" "+data+"?>"

  def default_start( self, name, attrs ):
    Debugging('START:', name)

  def default_end( self, name ):
    Debugging('END:', name)

  def error(self, e):
    raise e

  def fatalError(self, e):
    raise e

  def quiz_start( self, attrs ):
    self.root = Quiz()
    self.position = self.root
    self.position.title=attrs.get('title','default')
    self.position.bread_crumb=attrs.get('bread_crumb','default')
    self.position.src=attrs.get('src','default')

  def meta_start( self, attrs ):
    self.position.meta_list.append(attrs)
    Debugging("META start %s\n" % attrs)

  def link_start( self, attrs ):
    self.position.link_list.append(attrs)

  def quizlistitem_start( self, attrs ):
    self.position.quiz_list.append(attrs)

  def course_start( self, attrs ):
    self.position.course=attrs

  def question_start( self, attrs ):
    q = Question(self.position)
    self.position.question_list.append(q)
    self.position = q

  def text_end( self ):
    self.position.set_text(self.text)

  def choice_start( self, attrs ):
    if self.position.answer:
        sys.stderr.write("Processing halted. Multiple <choice>/<answer> tags\n")
        sys.exit(1)
    self.position.answer=Choice(self.position,attrs.get('type'),attrs.get('cols'))
    self.position = self.position.answer

  def answer_start( self, attrs ):
    if self.position.answer:
        sys.stderr.write("Processing halted. Multiple <choice>/<answer> tags\n")
        sys.exit(1)
    self.position.answer = Answer(self.position,attrs.get('value'))
    self.position = self.position.answer

  def tag_end( self ):
    self.position.tag = self.text.strip()

  def discussion_start( self, attrs ):
    d = Discussion(self.position,attrs.get('heading'))
    self.position.discussion_list.append(d)
    self.position = d

  def discussion_end( self ):
    self.position = self.position.parent

  def item_start( self, attrs ):
    r = Item(self.position,attrs.get('expect'))
    self.position.item_list.append(r)
    self.position = r

  def response_end( self ):
    self.position.response = self.text.strip()

  def when_right_end( self ):
    self.position.when_true = self.text.strip()

  def when_wrong_end( self ):
    self.position.when_false = self.text.strip()

  def item_end( self ):
    self.position = self.position.parent

  def answer_end( self ):
    self.position = self.position.parent

  def choice_end( self ):
    self.position = self.position.parent

  def question_end( self ):
    self.position = self.position.parent

  def quiz_end( self ):
    Debugging('level =', self.level)

# -----------------------------------------------------
#  DTD structure
# -----------------------------------------------------

# Each node of the document tree keeps a reference to its
# parent node in self.parent except for the root, which
# defaults to None

class Node(object):
  def __init__(self,parent = None):
    self.parent = parent
    self.meta_list = []
    self.link_list = []
    Debugging('Node: class={}, parent={}'.format(self.__class__.__name__,
        parent.__class__.__name__ if parent else ''))

  def accept(self,visitor):
    pass

  def broadcast(self,visitor):
    pass

  def __str__(self):
    return ''


class Quiz(Node):
  """<!ELEMENT quiz (title, bread_crumb, meta*, link*, question*)>
     <!ELEMENT title (#PCDATA)>
  """
  def __init__(self):
    Node.__init__(self)
    self.course=dict(name='', code='', url='', quizzes='', department='', university='')
    self.discussion_list = []
    self.link_list = []
    self.meta_list = []
    self.question_list = []
    self.quiz_list = []

  def accept(self,visitor):
    visitor.for_quiz(self)

  def broadcast(self,visitor):
    for node in self.question_list:
      node.accept(visitor)  

  def __str__(self):
    s = 'Quiz: %s\n' % self.title
    for p in self.question_list:
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
    visitor.for_discussion(self)

  def broadcast(self,visitor):
    for node in self.question_list:
      node.accept(visitor)  

  def set_text(self,text):
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

  def set_text(self,text):
    self.question = text.strip()

  def accept(self,visitor):
    visitor.for_question(self)

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
    self.item_list = []
    # --
    self.type = type
    self.cols = int(cols)

  def accept(self,visitor):
    visitor.for_choice(self)

  def broadcast(self,visitor):
    for node in self.item_list:
      node.accept(visitor)

  def __str__(self):
    s = "Choices:\n"
    for p in self.item_list:
      s += '%s\n' % str(p)
    return s


class Answer(Node):
  """<!ELEMENT answer (tag?, when_right, when_wrong)>
     <!ATTLIST answer value CDATA #REQUIRED>
     <!ELEMENT tag (#PCDATA)>
     <!ELEMENT when_right (#PCDATA)>
     <!ELEMENT when_wrong (#PCDATA)>
  """
  def __init__(self,parent,value):
    Node.__init__(self,parent)
    self.tag       = ""
    self.when_true  = ""
    self.when_false = ""
    # --
    self.value     = value

  def accept(self,visitor):
    visitor.for_answer(self)

  def __str__(self):
    s = self.value+': '
    if self.tag:
      s += self.tag
    s += '\n_right: %s Wrong:' % (self.when_true,self.when_false)
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

  def set_text(self,text):
    self.answer = text.strip()

  def accept(self,visitor):
    visitor.for_item(self)

  def __str__(self):
    s = '%s: %s' % (self.expect,self.answer)
    if self.response:
      s += '\n_response: ' + self.response
    return s


# =====================================================
# Visitor classes
# =====================================================

class node_visitor:
  """In the methods of this class, 'node' refers to the
  instance of the class calling the 'accept' method.  The
  general form of 'accept' is
  
         def accept(self,visitor):
           visitor.forXXX(self)
   
  In the method 'forXXX' of the visitor class, 'node' will
  refer to an instance of 'XXX'.
  """

  def for_quiz(self,node):
    node.broadcast(self)

  def for_discussion(self,node):
    node.broadcast(self)

  def for_question(self,node):
    node.broadcast(self)

  def for_choice(self,node):
    node.broadcast(self)

  def for_answer(self,node):
    pass

  def for_item(self,node):
    pass

# -----------------------------------------------------
class xml_writer(node_visitor):

#@-- Not presently used
  def element(self,node,tag):
    print(' <%s>'  % tag)
    node.broadcast(self)
    print(' </%s>' % tag)

  def for_quiz(self,node):
    print('<?xml version="1.0" encoding="iso-8859-1"?>')
    print('<!DOCTYPE quiz SYSTEM "mathquiz.dtd">' )
    print('<quiz>')
    for p in node.meta_list:
      s = '<meta'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print(s)
    for p in node.course:
      s = '<course'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print(s)
    for p in node.link_list:
      s = '<link'
      for q in p.keys():
        s += ' %s="%s"' % (q, p[q])
      s += '/>'
      print(s)
    print('<title>%s</title>' % node.title)
    node.broadcast(self)
    print('</quiz>')

  def for_question(self,node):
    print('<question>')
    print('<text><![CDATA[%s]]></text>' % strval(node.question))
    node.broadcast(self)
    print('</question>')

  def for_choice(self,node):
    print('  <choice type="%s" cols="%s">' % (node.type, node.cols))
    node.broadcast(self)
    print('  </choice>')

  def for_answer(self,node):
    print('    <answer value="%s">' % node.value)
    if node.tag:
      print('      <tag>%s</tag>' % strval(node.tag))
    print('      <when_right><![CDATA[%s]]></when_right>' % strval(node.when_true))
    print('      <when_wrong><![CDATA[%s]]></when_wrong>' % strval(node.when_false))
    print('    </answer>'  )
  
  def for_item(self,node):
    print('    <item expect="%s">' % node.expect)
    print('      <text><![CDATA[%s]]></text>' % strval(node.answer))
    if node.response:
      print('      <response><![CDATA[%s]]></response>' % strval(node.response))
    print('    </item>')
