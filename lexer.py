# lexer.py

# Token types
TT_NUMBER   = "NUMBER"
TT_STRING   = "STRING"
TT_IDENT    = "IDENT"
TT_KEYWORD  = "KEYWORD"
TT_SYMBOL   = "SYMBOL"
TT_EOF      = "EOF"

KEYWORDS = {
    "let", "print", "if", "else", "while",
    "true", "false", "fun", "return",
    "for", "in", "to"
}

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_     # IMPORTANT: no comma
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.col})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_char(self):
        nxt = self.pos + 1
        if nxt >= len(self.text):
            return None
        return self.text[nxt]

    def advance(self):
        if self.current_char() == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char().isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char() is not None and self.current_char() != "\n":
            self.advance()

    def number(self):
        start_line, start_col = self.line, self.col
        num_str = ""
        while self.current_char() is not None and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        return Token(TT_NUMBER, int(num_str), start_line, start_col)

    def string(self):
        # current char is opening "
        start_line, start_col = self.line, self.col
        self.advance()  # skip "
        chars = ""
        while self.current_char() is not None and self.current_char() != '"':
            # no escape handling for simplicity
            ch = self.current_char()
            if ch == "\n":
                raise Exception(f"Unterminated string at line {start_line}, col {start_col}")
            chars += ch
            self.advance()
        if self.current_char() != '"':
            raise Exception(f"Unterminated string at line {start_line}, col {start_col}")
        self.advance()  # skip closing "
        return Token(TT_STRING, chars, start_line, start_col)

    def identifier_or_keyword(self):
        start_line, start_col = self.line, self.col
        ident = ""
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == "_"):
            ident += self.current_char()
            self.advance()
        if ident in KEYWORDS:
            return Token(TT_KEYWORD, ident, start_line, start_col)
        return Token(TT_IDENT, ident, start_line, start_col)

    def generate_tokens(self):
        tokens = []
        while self.current_char() is not None:
            ch = self.current_char()

            if ch.isspace():
                self.skip_whitespace()
                continue

            if ch == "#":
                self.skip_comment()
                continue

            if ch.isdigit():
                tokens.append(self.number())
                continue

            if ch == '"':
                tokens.append(self.string())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self.identifier_or_keyword())
                continue

            # Multi-character operators: ==, !=, <=, >=
            if ch == "=" and self.peek_char() == "=":
                tokens.append(Token(TT_SYMBOL, "==", self.line, self.col))
                self.advance()
                self.advance()
                continue

            if ch == "!" and self.peek_char() == "=":
                tokens.append(Token(TT_SYMBOL, "!=", self.line, self.col))
                self.advance()
                self.advance()
                continue

            if ch == "<":
                if self.peek_char() == "=":
                    tokens.append(Token(TT_SYMBOL, "<=", self.line, self.col))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TT_SYMBOL, "<", self.line, self.col))
                    self.advance()
                continue

            if ch == ">":
                if self.peek_char() == "=":
                    tokens.append(Token(TT_SYMBOL, ">=", self.line, self.col))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TT_SYMBOL, ">", self.line, self.col))
                    self.advance()
                continue

            # Single-character symbols
            if ch in "=;+*-()/{}[],":   # added [ ] ,
                tokens.append(Token(TT_SYMBOL, ch, self.line, self.col))
                self.advance()
                continue

            raise Exception(f"Unexpected character '{ch}' at line {self.line}, col {self.col}")

        tokens.append(Token(TT_EOF, None, self.line, self.col))
        return tokens
        