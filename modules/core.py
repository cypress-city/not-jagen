import discord


def hex_color(hex_code: str):
    return discord.Colour(int(hex_code, 16))


def construct_embed(**kwargs) -> discord.Embed:
    ret = discord.Embed(
        title=kwargs.get("title"),
        description=kwargs.get("desc", kwargs.get("description")),
        color=kwargs.get("color"),
        url=kwargs.get("url")
    )
    fields = kwargs.get("fields", {})
    field_lines = kwargs.get("field_same_lines", {})
    for t, d in fields.items():
        ret.add_field(name=t, value=str(d), inline=field_lines.get(t, kwargs.get("same_line", True)))
    ret.set_thumbnail(url=kwargs.get("thumb"))
    ret.set_footer(text=kwargs.get("footer"))
    return ret


def red_embed(**kwargs):
    return construct_embed(color=hex_color("B33C30"), **kwargs)


def simplify_text(text: str):
    return "".join(c for c in text.lower() if c.isalnum())


def closeness(text: str, query: str):
    t = simplify_text(text)
    q = simplify_text(query)
    return 2 if t.startswith(q) else 1 if q in t else 0
