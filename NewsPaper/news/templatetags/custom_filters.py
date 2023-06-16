from django import template


register = template.Library()
WORD_BLACKLIST = {
    "редиска",
    "скипидар",
    "рубля",
    "сабля",
    "употреблять",
    "блямба",
    "команда",
    "подстрахуй",
    "lorem",
    "ipsum"
}


@register.filter()
def censor(text):
    text = text.split()
    for i, word in enumerate(text):
        print(text[i])
        if "".join(c for c in word.lower() if c.isalpha()) in WORD_BLACKLIST:
            text[i] = word[0] + "".join("*" for _ in word[1:-1]) + word[-1]
            print(text[i])
    return " ".join(text)
