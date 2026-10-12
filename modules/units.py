import discord
from discord.ext import commands
import json

from modules.bot import Bot
from modules.core import red_embed, closeness


TIER_NAMES = ["Base", "Beginner", "Specialty", "Advanced", "Master", "Divine"]
TIER_LEVELS = [1, 10, 20, 35, 45, 45]


class Stats:
    def __init__(self, stats: dict[str, int]):
        self.stats = stats

    def __add__(self, other):
        if isinstance(other, Stats):
            return Stats({g: self.stats[g] + other.stats[g] for g in self.stats})

    def display(self, include_percent: bool = False, include_avg: bool = False):
        r = " | ".join(f"{k} {v}{'' if (not include_percent) or k == 'Mov' else '%'}" for k, v in self.stats.items())
        if include_avg:
            r += f" (avg: {round(sum(self.stats.values()) / len(self.stats), 2)}{'%' if include_percent else ''})"
        return r


class Class:
    def __init__(self, name: str, tier: int, reqs: dict, growths: Stats, stat_bonuses: Stats, skills: list[str],
                 skill_growths: dict[str, int], mount: str | None):
        self.name = name
        self.tier = tier
        self.requirements = reqs
        self.growths = growths
        self.stat_bonuses = stat_bonuses
        self.skills = skills
        self.skill_growths = skill_growths
        self.mount = mount

    @staticmethod
    def from_json(js: dict):
        return Class(
            name=js["name"],
            tier=js["tier"],
            reqs=js["requirements"],
            growths=Stats(js["growths"]),
            stat_bonuses=Stats(js["stat_bonuses"]),
            skills=js["skills"],
            skill_growths=js["skill_growths"],
            mount=js["mount"]
        )

    def embed(self, bot: Bot):
        reqs = ""

        def format_reqs(r):
            return "\u2002".join(f"{bot.app_emojis[k.lower() + '_neutral']} {v}" for k, v in r.items())

        if self.requirements.get("primary"):
            reqs += f"Primary: **{format_reqs(self.requirements['primary'])}**"
        if self.requirements.get("secondary"):
            reqs += f"Secondary: **{format_reqs(self.requirements['secondary'])}**"
        fields = {
            "Tier": f"{TIER_NAMES[self.tier]} (Lv {TIER_LEVELS[self.tier]})",
            "Requirements": reqs.strip("\n"),
            "Growths": self.growths.display(include_percent=True),
            "Bonuses": self.stat_bonuses.display(),
            "Weapons": " ".join(str(bot.app_emojis[f"{g.lower()}_neutral"]) for g in self.skills),
            "Skill Growths": "\u2002".join(f"{bot.app_emojis[g.lower() + '_neutral']} +{j}"
                                           for g, j in self.skill_growths.items() if j)
        }
        if self.mount:
            fields["Mount"] = self.mount
        return red_embed(
            title=self.name,
            fields=fields,
            field_same_lines={"Growths": False, "Bonuses": False},
            same_line=True
        )


with open("data/classes.json", "r") as f:
    CLASSES = {k: Class.from_json(v) for k, v in json.load(f).items()}


class Unit:
    def __init__(self, name: str, starting_class: Class, growths: Stats, skills: dict[str, str],
                 equipped_class: Class = None):
        self.name = name
        self.starting_class = starting_class
        self.base_growths = growths
        self.skills = skills
        self.class_override = equipped_class

    @staticmethod
    def from_json(js: dict):
        return Unit(
            name=js["name"],
            starting_class=CLASSES[js["starting_class"]],
            growths=Stats(js["growths"]),
            skills=js["skills"]
        )

    def copy(self):
        return Unit(self.name, self.starting_class, self.base_growths, self.skills, self.class_override)

    @property
    def equipped_class(self):
        if self.class_override:
            return self.class_override
        else:
            return self.starting_class

    @property
    def growths(self):
        return self.base_growths + self.equipped_class.growths

    def embed(self, bot: Bot):
        return red_embed(
            title=f"{self.name}",
            desc=f"Class: {self.equipped_class.name}",
            fields={
                "Growths": self.growths.display(include_percent=True, include_avg=True),
                "Skills": " ".join(str(bot.app_emojis[f"{g.lower()}_{j.lower()}"]) for g, j in self.skills.items())
            },
            same_line=False
        )


with open("data/units.json", "r") as f:
    UNITS = {k: Unit.from_json(v) for k, v in json.load(f).items()}


async def unit_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in UNITS if closeness(g, current)], key=lambda c: -closeness(c, current))
    return [discord.app_commands.Choice(name=g, value=g) for g in matches][:25]


async def class_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in CLASSES if closeness(g, current)], key=lambda c: -closeness(c, current))
    return [discord.app_commands.Choice(name=g, value=g) for g in matches][:25]


class UnitsCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="unit",
        description="Shows info about a unit."
    )
    @discord.app_commands.autocomplete(unit=unit_autocomplete, as_class=class_autocomplete)
    @discord.app_commands.describe(unit="Unit name", as_class="Class name")
    @discord.app_commands.rename(as_class="class")
    async def unit_command(self, i: discord.Interaction, unit: str, as_class: str = None):
        if not (unit := UNITS.get(unit)):
            return await i.response.send_message("⚠️ Unit not found", ephemeral=True)

        unit = unit.copy()
        if as_class := CLASSES.get(as_class):
            unit.class_override = as_class

        return await i.response.send_message(embed=unit.embed(self.bot))

    @discord.app_commands.command(
        name="class",
        description="Shows info about a class."
    )
    @discord.app_commands.autocomplete(class_name=class_autocomplete)
    @discord.app_commands.describe(class_name="Class name")
    @discord.app_commands.rename(class_name="class")
    async def class_command(self, i: discord.Interaction, class_name: str):
        if not (cl := CLASSES.get(class_name)):
            return await i.response.send_message("⚠️ Class not found", ephemeral=True)

        return await i.response.send_message(embed=cl.embed(self.bot))


async def setup(bot: Bot):
    await bot.add_cog(UnitsCog(bot))
