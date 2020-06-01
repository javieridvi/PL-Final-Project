import ply.lex as lex
import ply.yacc as parser
from ply.lex import TOKEN
import sys
from Menu import ConsoleMenu


class FileReader():
    @staticmethod
    def get_file_contents():
        current_file = open('datafile.txt', 'r')
        content = current_file.read()
        current_file.close()
        return content


##############################################
# Lexer
##############################################

class Lexer():
    reserved = {
        'connect': 'CONNECT',
        'quit': 'QUIT',
        'send': 'SEND',
        'help': 'HELP',
        'start': 'START'
    }

    tokens = [
                 'IP',
                 'COMMENT',
                 'NUMBER',
                 'ID',
                 'MOD',
                 'PLUS',
                 'MINUS',
                 'MULTIPLY',
                 'DIVIDE',
                 'LPARENT',
                 'RPARENT',
                 'LBRACKET',
                 'RBRACKET',
                 'NOTEQ',
                 'EQCOMPARE',
                 'EQUALS',
                 'DEFINE',
                 'GREATERTHAN',
                 'LESSTHAN',
                 'RESERV'

             ] + list(reserved.values())

    t_RESERV = r'NOW'
    t_DEFINE = r':='
    t_PLUS = r'[+]'
    t_MINUS = r'[-]'
    t_MULTIPLY = r'[*]'
    t_DIVIDE = r'[/]'
    t_MOD = r'[%]'
    t_LPARENT = r'[(]'
    t_RPARENT = r'[)]'
    t_LBRACKET = r'[{]'
    t_RBRACKET = r'[}]'
    t_EQUALS = r'='
    t_GREATERTHAN = r'[>]'
    t_LESSTHAN = r'[<]'

    ip_address = r'[0-9]{3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}'
    t_ignore = ' \t\n\r\f\v'
    number = r'[0-9]+'
    identifier = r'[a-zA-Z0-9]+'
    comment = r'[$].*'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    @TOKEN(ip_address)
    def t_IP(self, t):
        return t

    @TOKEN(number)
    def t_NUMBER(self, t):
        t.value = int(t.value)
        return t

    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, 'ID')
        return t

    @TOKEN(comment)
    def t_COMMENT(self, t):
        pass

    def t_error(self, t):
        pass

    def test(self, data: str):
        self.lexer.input(data)
        while True:
            token = self.lexer.token()
            if token:
                print(token)
            else:
                break


##############################################
# Parser
##############################################

class Parser():
    tokens = Lexer.tokens

    def __init__(self):
        self.lexer = Lexer()
        self.parser = parser.yacc(module=self)
        self.menu = None

    def parse(self, data: str):
        self.verify_menu
        return self.parser.parse(data, self.lexer)

    def set_menu(self, menu: ConsoleMenu):
        self.menu = menu

    def verify_menu(self):
        if not self.menu:
            print("No menu manager set")
            sys.exit(1)

    precedence = (
        ('nonassoc', 'EQUALS', 'EQCOMPARE', 'NOTEQ', 'GREATERTHAN', 'LESSTHAN'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD')
    )

    def p_statement(self, p):
        '''statement : quit
                     | words
                     | sum
                     | start_server
                     | connect'''
        p[0] = p[1]

    def p_connect(self, p):
        '''connect : CONNECT IP NUMBER'''
        self.menu.connect_to_server(p[2], p[3])

    def p_start_server(self, p):
        '''start_server : START IP NUMBER'''
        p[0] = p[1]
        self.menu.create_server(p[2], p[3])

    def p_sum(self, p):
        '''sum : NUMBER PLUS NUMBER'''
        p[0] = p[1] + p[3]

    def p_quit(self, p):
        '''quit : QUIT RESERV'''
        p[0] = p[1] + p[2]
        self.menu.quit_program()

    def p_words(self, p):
        '''words : ID
                 | words
                 | words ID'''
        if len(p) == 2:
            p[0] = ' ' + p[1]
        elif len(p) == 3:
            p[0] = ' ' + p[1] + ' ' + p[2]

    def p_send(self, p):
        '''send : SEND words'''
        p[0] = p[2]

    def p_error(self, p):
        pass


