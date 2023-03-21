# encoding: utf-8

'''My own template engine.
    Format string with special template syntax.
    Pass a template string to the Template class you can then call the render
    method to get the resulting text.

    The template string is first converted into a list of tokens of the
    Token class with an attibute Token.token_type which can either be
    TokenType.TEXT for text tokens, TokenType.VAR for _var tokens
    TokenType.COMMENT for coments and TokenType.BLOCK for block tokens

    The tokens can then be feed to the Parser which returns a list
    of Node objects on call to it's *render* method.

    Each Node object generates it's contents on call to it's render method.

    so:
        Tokeniser(template_string)
            |
            \/
        tokenise() --> [text-token, var-token, ... tokens]
            |
            \/
        Parser(tokens).render(context)
            |
            \/
            Nodes   [TextNode, _VarNode, ... Nodes]
            |
            \/
        call node.render()
        boom * rendered template
'''

import re
import string # for whitespace


# debugging
import sys
import warnings
from enum import Enum, auto
from pprint import pprint

stop = sys.exit


class TemplateError(Exception):
    pass


class ExpressionError(TemplateError):
    pass

__all__ = ['Template']
__version__ = '1.0'

BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'
COMMENT_TAG_START = '{#'
COMMENT_TAG_END = '#}'
VARIABLE_TAG_START = '{{'
VARIABLE_TAG_END = '}}'



# match any of the node_types
placeholder_re =re.compile("(\{\%.*?\%\}"  # try to match a block {% for ...%}
                    '|\{\{.*?\}\}'	# then match a variable {{ var }}
                    '|\{\#.*?\#\})'	# then match a comment {# comment #}
                    )

tell_line = lambda token: "at {} line".format(_get_pos(token.lineno))

def _split(str_):
    # split a str by an empty string
    return [i for i in str_]


def _get_pos(num):
    s = str(num)
    d = {'1': 'st', '2': 'nd', '3': 'rd'}
    for i in range(4, 21):
        if s.endswith(str(i)):
            return s+'th'
    for i in d:
        if s.endswith(str(i)):
            return s+d[i]
    return 'th'


def stat(tokens, filter=None):
    import pprint as p
    result = []
    filter = filter.upper() if filter else ''
    if filter and filter in ('TEXT', 'VAR', 'BLOCK', 'COMMENT'):
        p.pprint([(token.token_type.name, token.contents) for token in tokens if token.token_type.name == filter])
    else:
        p.pprint([(token.token_type.name, token.contents) for token in tokens])


class Expression:
    '''This will attempt to resolve an expression.
    
    *token*: str or Token
    Note that an expression is assumed to be a variable {{ var }}
    or method {{ var.method }} {{ var.x }}
    when a method is to be accessed it is called without arguments
    '''
    def __init__(self, token):
        if hasattr(token, 'contents'):
            expression = token.contents
            self.token = token
        else: # token is a string
            expression = str(token)
            self.token = None
        self.expression = str(expression).strip(string.whitespace + '.')
    
    def resolve(self, context):
        exp = self.expression.split('.')
        try:
            first = exp.pop(0)
            value = context[first]
            for indx, variable in enumerate(exp):
                try:
                    attrib = getattr(value, variable)
                except AttributeError:
                    self.error('AttributeError: <%s> has not attribute named <%s>'%(variable, value))
                if callable(attrib):
                    value = attrib() # catch TypeError for insufficient arguments
        except KeyError as ex:
            self.error('NameError: "%s" does not exists in context', ex)
        return value
    
    def error(self, e, former_stack=None):
        if self.token:
            e += " '%s' [%s]" % (self.expression, tell_line(self.token))
        if former_stack:
            raise ExpressionError(e) from former_stack
        raise ExpressionError(e)


  
################################################################################
## tokens #######################################################################


class TokenType(Enum):
    TEXT = auto()
    VAR = auto()
    BLOCK = auto()
    COMMENT = auto()

    def __repr__(self):
        return "<TokenType '%s'>"%(self.name.lower())


class Token:
    '''Represent visual segment of a string.
    
    *token_type* is an attribute of TokenType eg. TokenType.COMMENT which 
    represents a comment there for contents is within the delimiter and lineno
    is the well... lineno
    Token(TokenType.COMMENT, 'Some comments', 5)
    '''
    def __init__(self, token_type, contents, lineno):
        self.token_type = token_type
        self.contents = contents
        self.lineno = lineno

    def __repr__(self):
        return "<Token type:'%s' lineno:'%s' at %s>"%(self.token_type.name.lower(), _get_pos(self.lineno), str(hex(id(self))))


class Tokeniser:
    '''Creates tokens from *template_string*.'''
    # Note for now tokens that do not start and end with thier delimiter
    # are ignored
    def __init__(self, template_string):
        self.template_string = template_string
        self.debug = True

    def tokenise(self):
        '''Gather all tokens an return it.'''
        unparsed_tokens = self.split()
        
        tokens = []
        lineno = 1
        for bit in unparsed_tokens:
            if bit:
                token = self.get_token(bit, lineno)
                tokens.append(token)
            lineno += bit.count('\n')
            
        # if self.debug:
        #     'self.gather_tokens()'
        #     # print('done serving tokens from Tokeniser')
        #     # stat(tokens)
        return tokens
    
    def split(self):
        return placeholder_re.split(self.template_string)
    
    def get_token(self, bit, lineno):
        '''Returns a token using a token string.'''
        if bit.startswith(VARIABLE_TAG_START):
            return Token(TokenType.VAR,
                         self.get_contents(bit, VARIABLE_TAG_END),
                         lineno)
        elif bit.startswith(COMMENT_TAG_START):
            return Token(TokenType.COMMENT,
                         self.get_contents(bit, COMMENT_TAG_END),
                         lineno)
        elif bit.startswith(BLOCK_TAG_START):
            return Token(TokenType.BLOCK,
                         self.get_contents(bit, BLOCK_TAG_END),
                         lineno)
        else:
            return Token(TokenType.TEXT, bit, lineno)
        
    def get_contents(self, bit, end):
        if bit.endswith(end):
            return bit[2:-2].strip()
        # else:
        #     parser should do something like
        #     if '{{' in token.contents:
        #         raise TemplateError
        # but for now strange looking tags are ignored
        return bit


################################################################################
## nodes #######################################################################

# There are no comment nodes since they don't have
# to render any thing


class TextNode:
    def __init__(self, s):
        self.s = s

    def render(self, context):
        '''text node do not need any more rendering'''
        return self.s


class VariableNode:
    def __init__(self, expression):
        self.expression = expression
        
    def render(self, context):
        return str(self.expression.resolve(context))


class BlockHelper:
    '''help in block parsing'''
    registered_blocks = ('for', 'if')
    singletons = () # tags that do not required end blocks
    
    def __init__(self, block_token):
        self.block_token = block_token
        self.block_name = self.get_block_name(block_token)
        
        if self.block_name not in (self.registered_blocks + self.singletons):
            raise TemplateError("Invalid block: the block '%s' is not supported [%s]"%(self.block_name, tell_line(block_token)))
        
        self.is_singleton = self._requires_endblock()
        if self._requires_endblock:
            self.endblock = self._get_endblock()
        
    def _get_endblock(self):
        return 'end' + self.block_name
    
    def _requires_endblock(self):
        if self.block_name in self.singletons:
            return True # singleton blocks don't need end block
        else:
            return False
        
    @staticmethod
    def get_block_name(block_token):
        '''Returns the block name of a block.
        
        This is the first word in the block
        {% for...%} <for> is the block name.'''
        
        try:
            block_name = block_token.contents.split()[0]
            return block_name
        except IndexError:
            raise TemplateError('Empty block %s'%(block_token.contents))


class BlockNode: # this class should be private as it's args depend on the program
    def __init__(self, block_tokens):
        self.block_tokens = block_tokens
        self.blockname = self.get_block_name(self.block_tokens[0])
        
    def render(self, context):
        blockname = self.blockname
        mname = 'do_'+blockname
        method = getattr(self, mname)
        return method(context.copy())
    
    def _render(self, nodes, context):
        return ''.join([str(node.render(context)) for node in nodes])
    
    def do_for(self, context):
        '''for <vars> in <iterable> [reverse]
        <var> will be introduced into context and will be rendered
        <vars> :: a, b
        n number of times depending on <iterable>
        '''
        context = context
        block_head = self.block_tokens[0].contents.strip()
        # some serious parsing is about to take place
        statement = block_head[3:] # <for> excluded
        try:
            in_ = statement.index('in')
        except ValueError:
            raise # appropriate error msg will be displayed 
        loop_vars = statement[:in_].strip().split(',')
        iteration = statement[in_+2:].strip().split() # *2* here gets us pass the *in* str
        # print(loop_vars, iteration)
        if not iteration or not loop_vars[0]:
            raise
        reverse = len(iteration) == 2 and iteration[1].lower() == 'reverse'
        iter = context[iteration[0]]
        if reverse:
            iter = reversed(iter)
        # render
        res_nodes = []
        for item in iter:
            if len(loop_vars) > 1:
                for i, var in enumerate(loop_vars):
                    context[var] = item[i]
                
            else:
                context[loop_vars[0]] = item
            for_tokens = self.block_tokens[1:-1]
            inner_nodes = Parser(for_tokens).parse()
            res_nodes.append(TextNode(self._render(inner_nodes, context)))
        return self._render(res_nodes, context)
    
    def do_if(self, context):
        '''based on codition.'''
        startblock = self.block_tokens[0]
        if_context = self.block_tokens[1:-1] # from {%if..%} to {%endif%} not including delimiters
        else_context = []
        # this will cut out else context if any
        for indx, token in enumerate(self.block_tokens):
            if token.token_type == TokenType.BLOCK and BlockHelper.get_block_name(token) == 'else':
                else_context.extend(self.block_tokens[indx+1:-1])
                if_context = self.block_tokens[1:indx]
        # stat(if_context)
        # stat(else_context)
        try:
            condition = Expression(startblock.contents.split()[1]).resolve(context)
        except IndexError:
            raise TemplateError('no condition for if')
        if condition:
            context_to_parse = if_context
        else:
            context_to_parse = else_context
        nodes = Parser(context_to_parse).parse()
        return ''.join([str(node.render(context)) for node in nodes])
    
    def get_block_name(self, token):
        return BlockHelper.get_block_name(token)
    

class Parser:
    '''Converts tokens into Nodes and render them.
    
    Each node generates it's own contents when rendered the job of this class
    is to make figure out which node and what it will need for it's job.
    '''
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        '''Returns a node list.'''
        nodes = []
        finding_end_block = False   # when this is True find a block named *end_block*
        block_tokens = []           # from <startblock> to <endblock>
        end_block = None            # end block to find
        # a block can contain other blocks, in other not to confuse their <endblock>s
        # as THE end block any similar child block found will increment *locals* when their 
        # closing block is found this will decrement
        # if a closing block is found and this is 0 it is assumed to be the end block for this scope
        locals = 0  # If an endblock is found and (locals != 0) then it's not found
        
        for token in self.tokens:
            if not finding_end_block:
                if token.token_type == TokenType.TEXT:
                    nodes.append(TextNode(token.contents))
                elif token.token_type == TokenType.VAR:
                    if not token.contents:
                        raise TemplateError('Empty variable cannot substitute')
                    else:
                        nodes.append(VariableNode(Expression(token)))
                elif token.token_type == TokenType.COMMENT:
                    pass # roses a blue comments are gone and so is yours :)
                elif token.token_type == TokenType.BLOCK:
                    blockinfo = BlockHelper(token)
                    if blockinfo.is_singleton:
                        pass
                    else:
                        finding_end_block = True
                        block_tokens.clear()
                        block_tokens.append(token)
                        end_block = blockinfo.endblock
                    
            else:
                if token.token_type == TokenType.BLOCK:
                    block_name = BlockHelper.get_block_name(token)
                    if block_name == blockinfo.block_name:
                        locals += 1
                    elif block_name == end_block:
                        if locals == 0:
                            block_tokens.append(token) # need to append else block from here
                            nodes.append(BlockNode(block_tokens[:])) # or it won't get into the BlockNode
                            finding_end_block = False
                            end_block = None
                            continue
                        else:
                            locals -= 1
                block_tokens.append(token) # note token not parsed
        
        # finished parsing check for unfinished tags
        if finding_end_block:
            startblock = block_tokens[0]
            raise TemplateError("Could not find endblock for (%s) [%s]"%(startblock.contents,
                                                                          tell_line(startblock)))
        return nodes
                


class Template:
    def __init__(self, template_string):
        self.template_string = str(template_string)
        
    def render(self, context):
        '''render the *template_string*.
        similar to 
        ''.join([str(node.render(context)) for node in Parser(Tokeniser(template_string).tokenise()).parse()])
        '''
        tokens = Tokeniser(self.template_string).tokenise()
        parser = Parser(tokens)
        nodes = parser.parse()
        return ''.join([node.render(context) for node in nodes])


template = (
    '''\
    this is a {{ variabvarle }}
        {% if online %}
            on line
            {%else%}
            not online
        {% endif %}
        
        {% for i in x%}
            the current item is {{ i }}
        {% endfor %}
    '''
)
context = {
            'variable': 'value',
            'online': True, # times
            'iswilliams': True,
            'x': ['beans', 'tomato', 'handsome'],
        }
# print(template.render(context))
#tk = Tokeniser(template).tokenise()
#pprint(Parser(tk).parse())
